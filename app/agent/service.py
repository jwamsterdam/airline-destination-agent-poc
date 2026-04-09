from typing import Callable, List, Optional

from app.agent.llm import OpenAITravelInterpreter
from app.agent.parser import COUNTRY_ALIASES, SEASON_KEYWORDS, TRIP_TAG_PRIORITY, parse_user_query
from app.agent.tool import get_destinations
from app.agent.types import (
    AgentQueryResponse,
    ChatMessage,
    DestinationFilters,
    DestinationResult,
    LLMAvailability,
    ParsedQuery,
)

ALLOWED_COUNTRIES = set(COUNTRY_ALIASES.values())
ALLOWED_PRICE_CATEGORIES = {"budget", "mid_range", "premium"}
ALLOWED_SEASONS = set(SEASON_KEYWORDS.keys())
ALLOWED_TRIP_TAGS = set(TRIP_TAG_PRIORITY)
SUPPORTED_RESPONSE_LANGUAGES = {"en", "nl", "fr"}


class AgentService:
    def __init__(
        self,
        graphql_endpoint_url: str,
        default_limit: int = 5,
        llm_enabled: bool = True,
        llm_model: str = "gpt-4o-mini",
        destination_fetcher: Optional[
            Callable[[DestinationFilters, str], List[DestinationResult]]
        ] = None,
        query_interpreter: Optional[object] = None,
    ) -> None:
        self.graphql_endpoint_url = graphql_endpoint_url
        self.default_limit = default_limit
        self.llm_enabled = llm_enabled
        self.destination_fetcher = destination_fetcher or get_destinations
        self.query_interpreter = query_interpreter or OpenAITravelInterpreter(model=llm_model)

    def run(
        self,
        message: str,
        limit: Optional[int] = None,
        chat_history: Optional[List[ChatMessage]] = None,
        response_language: Optional[str] = None,
    ) -> AgentQueryResponse:
        selected_language = normalize_response_language(response_language)
        parsed_query = self._parse_query(message=message, chat_history=chat_history or [])
        applied_filters = parsed_query.filters

        if not applied_filters.has_filters():
            return AgentQueryResponse(
                original_query=message,
                applied_filters=applied_filters,
                matched_terms=parsed_query.matched_terms,
                answer=get_text("clarification", selected_language),
                destinations=[],
            )

        destinations = self.destination_fetcher(applied_filters, self.graphql_endpoint_url)
        result_limit = limit or self.default_limit
        trimmed_destinations = destinations[:result_limit]
        answer = self._compose_answer(
            original_query=message,
            applied_filters=applied_filters,
            destinations=trimmed_destinations,
            chat_history=chat_history or [],
            response_language=selected_language,
        )

        return AgentQueryResponse(
            original_query=message,
            applied_filters=applied_filters,
            matched_terms=parsed_query.matched_terms,
            answer=answer,
            destinations=trimmed_destinations,
        )

    def llm_availability(self) -> LLMAvailability:
        if not self.llm_enabled:
            return LLMAvailability(enabled=False, reason="LLM support is disabled by configuration.")
        if not self.query_interpreter.is_available():
            return LLMAvailability(
                enabled=False,
                reason=self.query_interpreter.unavailable_reason(),
            )
        return LLMAvailability(enabled=True)

    def _parse_query(self, message: str, chat_history: List[ChatMessage]) -> ParsedQuery:
        rules_parsed = parse_user_query(message)

        if self.llm_enabled and self.query_interpreter.is_available():
            try:
                llm_parsed = self.query_interpreter.parse_query(message=message, chat_history=chat_history)
                return self._merge_with_rule_fallback(llm_parsed=llm_parsed, rules_parsed=rules_parsed)
            except Exception:
                return rules_parsed
        return rules_parsed

    def _compose_answer(
        self,
        original_query: str,
        applied_filters: DestinationFilters,
        destinations: List[DestinationResult],
        chat_history: List[ChatMessage],
        response_language: str,
    ) -> str:
        if destinations and self.llm_enabled and self.query_interpreter.is_available():
            try:
                return self.query_interpreter.summarize_results(
                    original_query=original_query,
                    applied_filters=applied_filters,
                    destinations=destinations,
                    chat_history=chat_history,
                    response_language=response_language,
                )
            except Exception:
                pass

        filter_summary = self._describe_filters(applied_filters)

        if not destinations:
            return get_text("no_results", response_language).format(filter_summary=filter_summary)

        destination_summary = ", ".join(
            f"{destination.destination_name}, {destination.destination_country} "
            f"(from EUR {destination.estimated_from_price_eur:.0f})"
            for destination in destinations
        )
        return get_text("matches_found", response_language).format(
            filter_summary=filter_summary,
            destination_summary=destination_summary,
        )

    def _describe_filters(self, applied_filters: DestinationFilters) -> str:
        descriptions = []

        if applied_filters.country:
            descriptions.append(f"country {applied_filters.country}")
        if applied_filters.season:
            descriptions.append(f"{applied_filters.season} travel")
        if applied_filters.trip_tag:
            descriptions.append(f"{humanize_trip_tag(applied_filters.trip_tag)} preferences")
        if applied_filters.max_price is not None:
            descriptions.append(f"a budget up to EUR {applied_filters.max_price:.0f}")
        if applied_filters.min_price is not None:
            descriptions.append(f"a minimum budget of EUR {applied_filters.min_price:.0f}")
        if applied_filters.price_category:
            descriptions.append(f"{applied_filters.price_category} pricing")

        if not descriptions:
            return "the available destination filters"

        return ", ".join(descriptions)

    def _merge_with_rule_fallback(
        self,
        llm_parsed: ParsedQuery,
        rules_parsed: ParsedQuery,
    ) -> ParsedQuery:
        llm_filters = llm_parsed.filters
        rule_filters = rules_parsed.filters

        merged_filters = DestinationFilters(
            country=self._pick_valid_value(llm_filters.country, rule_filters.country, ALLOWED_COUNTRIES),
            min_price=self._pick_numeric_value(llm_filters.min_price, rule_filters.min_price),
            max_price=self._pick_numeric_value(llm_filters.max_price, rule_filters.max_price),
            price_category=self._pick_valid_value(
                llm_filters.price_category,
                rule_filters.price_category,
                ALLOWED_PRICE_CATEGORIES,
            ),
            trip_tag=self._pick_valid_value(llm_filters.trip_tag, rule_filters.trip_tag, ALLOWED_TRIP_TAGS),
            season=self._pick_valid_value(llm_filters.season, rule_filters.season, ALLOWED_SEASONS),
        )

        return ParsedQuery(
            filters=merged_filters,
            matched_terms=merge_unique_terms(llm_parsed.matched_terms, rules_parsed.matched_terms),
        )

    def _pick_valid_value(
        self,
        llm_value: Optional[str],
        fallback_value: Optional[str],
        allowed_values: set,
    ) -> Optional[str]:
        if llm_value in allowed_values:
            return llm_value
        if fallback_value in allowed_values:
            return fallback_value
        return None

    def _pick_numeric_value(
        self,
        llm_value: Optional[float],
        fallback_value: Optional[float],
    ) -> Optional[float]:
        if llm_value is not None and llm_value >= 0:
            return llm_value
        if fallback_value is not None and fallback_value >= 0:
            return fallback_value
        return None


def humanize_trip_tag(trip_tag: str) -> str:
    return trip_tag.replace("_", " ")


def merge_unique_terms(*term_groups: List[str]) -> List[str]:
    merged_terms: List[str] = []
    for term_group in term_groups:
        for term in term_group:
            if term not in merged_terms:
                merged_terms.append(term)
    return merged_terms


def normalize_response_language(response_language: Optional[str]) -> str:
    if response_language in SUPPORTED_RESPONSE_LANGUAGES:
        return response_language
    return "en"


TEXTS = {
    "clarification": {
        "en": (
            "I could not confidently map your request to the available filters yet. "
            "Try mentioning a season, country, budget, or trip type such as beach or city trip."
        ),
        "nl": (
            "Ik kon je vraag nog niet betrouwbaar omzetten naar de beschikbare filters. "
            "Noem bijvoorbeeld een seizoen, land, budget of type reis zoals strand of stedentrip."
        ),
        "fr": (
            "Je ne peux pas encore traduire votre demande de maniere fiable vers les filtres disponibles. "
            "Mentionnez par exemple une saison, un pays, un budget ou un type de voyage comme plage ou city trip."
        ),
    },
    "no_results": {
        "en": (
            "I interpreted your request as {filter_summary}, but no destinations matched those filters. "
            "Try relaxing the budget, season, or trip type."
        ),
        "nl": (
            "Ik heb je vraag geinterpreteerd als {filter_summary}, maar er zijn geen bestemmingen gevonden die hierbij passen. "
            "Probeer het budget, seizoen of type reis wat ruimer te maken."
        ),
        "fr": (
            "J'ai interprete votre demande comme {filter_summary}, mais aucune destination ne correspond a ces filtres. "
            "Essayez d'elargir un peu le budget, la saison ou le type de voyage."
        ),
    },
    "matches_found": {
        "en": "I interpreted your request as {filter_summary}. Here are some matching destinations: {destination_summary}.",
        "nl": "Ik heb je vraag geinterpreteerd als {filter_summary}. Hier zijn een paar passende bestemmingen: {destination_summary}.",
        "fr": "J'ai interprete votre demande comme {filter_summary}. Voici quelques destinations correspondantes : {destination_summary}.",
    },
}


def get_text(key: str, language: str) -> str:
    return TEXTS[key].get(language, TEXTS[key]["en"])
