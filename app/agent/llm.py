import json
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.agent.types import ChatMessage, DestinationFilters, DestinationResult, ParsedQuery


INTENT_SYSTEM_PROMPT = """
You are an airline destination query interpreter.
Extract only the supported GraphQL filters from the traveler request.

Rules:
- Only use these filter fields: country, min_price, max_price, price_category, trip_tag, season.
- Leave fields null when the request does not clearly imply them.
- Use only these trip_tag values when applicable:
  beach, sunny_escape, citytrip, cultural, nature, active, family_friendly,
  romantic, foodie, nightlife, island, winter_holiday
- Use only these season values when applicable: spring, summer, autumn, winter
- Never map generic "winter" to winter_holiday.
- Only use winter_holiday when winter sports intent is explicit, such as ski, skiing, snowboard, snowboarding, winter sports, or wintersport.
- Normalize Dutch country aliases like Spanje to Spain and Griekenland to Greece.
- matched_terms should contain a short list of the words or phrases that drove the interpretation.
- Do not invent filters outside the request.
""".strip()

SUMMARY_SYSTEM_PROMPT = """
You are a travel recommendation assistant for an airline demo.
Use the supplied destination results only.
Explain the best matches conversationally and clearly.
If no destinations are supplied, explain that no matches were found and suggest relaxing budget, season, or trip type.
Do not invent destinations or prices.
""".strip()

LANGUAGE_NAMES = {
    "en": "English",
    "nl": "Dutch",
    "fr": "French",
}


class LLMParsedQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_category: Optional[str] = None
    trip_tag: Optional[str] = None
    season: Optional[str] = None
    matched_terms: List[str] = []


class OpenAITravelInterpreter:
    def __init__(self, model: str) -> None:
        self.model = model
        self._client = None
        self._init_error = None

        try:
            from openai import OpenAI

            self._client = OpenAI()
        except Exception as exc:  # pragma: no cover - environment dependent
            self._init_error = str(exc)

    def is_available(self) -> bool:
        return self._client is not None

    def unavailable_reason(self) -> Optional[str]:
        return self._init_error

    def parse_query(self, message: str, chat_history: Optional[List[ChatMessage]] = None) -> ParsedQuery:
        if self._client is None:
            raise RuntimeError(self._init_error or "OpenAI client is unavailable.")

        response = self._client.responses.parse(
            model=self.model,
            input=build_messages(
                system_prompt=INTENT_SYSTEM_PROMPT,
                message=message,
                chat_history=chat_history or [],
            ),
            text_format=LLMParsedQuery,
        )
        parsed = response.output_parsed
        filters = DestinationFilters(
            country=parsed.country,
            min_price=parsed.min_price,
            max_price=parsed.max_price,
            price_category=parsed.price_category,
            trip_tag=parsed.trip_tag,
            season=parsed.season,
        )
        return ParsedQuery(filters=filters, matched_terms=parsed.matched_terms)

    def summarize_results(
        self,
        original_query: str,
        applied_filters: DestinationFilters,
        destinations: List[DestinationResult],
        chat_history: Optional[List[ChatMessage]] = None,
        response_language: Optional[str] = None,
    ) -> str:
        if self._client is None:
            raise RuntimeError(self._init_error or "OpenAI client is unavailable.")

        prompt = build_summary_prompt(
            original_query=original_query,
            applied_filters=applied_filters,
            destinations=destinations,
            response_language=response_language,
        )
        response = self._client.responses.create(
            model=self.model,
            input=build_messages(
                system_prompt=SUMMARY_SYSTEM_PROMPT,
                message=prompt,
                chat_history=chat_history or [],
            ),
        )
        return response.output_text.strip()


def build_messages(system_prompt: str, message: str, chat_history: List[ChatMessage]) -> List[dict]:
    messages = [{"role": "system", "content": system_prompt}]
    for chat_message in chat_history:
        messages.append({"role": chat_message.role, "content": chat_message.content})
    messages.append({"role": "user", "content": message})
    return messages


def build_summary_prompt(
    original_query: str,
    applied_filters: DestinationFilters,
    destinations: List[DestinationResult],
    response_language: Optional[str] = None,
) -> str:
    payload = {
        "original_query": original_query,
        "applied_filters": applied_filters.model_dump(exclude_none=True),
        "destinations": [destination.model_dump() for destination in destinations],
        "response_language": LANGUAGE_NAMES.get(response_language or "en", "English"),
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)
