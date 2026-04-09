from typing import Callable, List, Optional

from app.agent.llm import OpenAITravelInterpreter
from app.agent.parser import parse_user_query
from app.agent.tool import get_destinations
from app.agent.types import (
    AgentQueryResponse,
    ChatMessage,
    DestinationFilters,
    DestinationResult,
    LLMAvailability,
    ParsedQuery,
)


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
    ) -> AgentQueryResponse:
        parsed_query = self._parse_query(message=message, chat_history=chat_history or [])
        applied_filters = parsed_query.filters

        if not applied_filters.has_filters():
            return AgentQueryResponse(
                original_query=message,
                applied_filters=applied_filters,
                matched_terms=parsed_query.matched_terms,
                answer=(
                    "I could not confidently map your request to the available filters yet. "
                    "Try mentioning a season, country, budget, or trip type such as beach or city trip."
                ),
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
        if self.llm_enabled and self.query_interpreter.is_available():
            try:
                return self.query_interpreter.parse_query(message=message, chat_history=chat_history)
            except Exception:
                return parse_user_query(message)
        return parse_user_query(message)

    def _compose_answer(
        self,
        original_query: str,
        applied_filters: DestinationFilters,
        destinations: List[DestinationResult],
        chat_history: List[ChatMessage],
    ) -> str:
        if self.llm_enabled and self.query_interpreter.is_available():
            try:
                return self.query_interpreter.summarize_results(
                    original_query=original_query,
                    applied_filters=applied_filters,
                    destinations=destinations,
                    chat_history=chat_history,
                )
            except Exception:
                pass

        filter_summary = self._describe_filters(applied_filters)

        if not destinations:
            return (
                f"I interpreted your request as {filter_summary}, but no destinations matched those filters. "
                "Try relaxing the budget, season, or trip type."
            )

        destination_summary = ", ".join(
            f"{destination.destination_name}, {destination.destination_country} "
            f"(from EUR {destination.estimated_from_price_eur:.0f})"
            for destination in destinations
        )
        return (
            f"I interpreted your request as {filter_summary}. "
            f"Here are some matching destinations: {destination_summary}."
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


def humanize_trip_tag(trip_tag: str) -> str:
    return trip_tag.replace("_", " ")
