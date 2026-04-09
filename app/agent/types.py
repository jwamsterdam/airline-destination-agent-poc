from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str
    content: str


class DestinationFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_category: Optional[str] = None
    trip_tag: Optional[str] = None
    season: Optional[str] = None

    def has_filters(self) -> bool:
        return any(value is not None for value in self.model_dump().values())

    def to_graphql_variables(self) -> dict:
        variables = {}
        mapping = {
            "country": self.country,
            "minPrice": self.min_price,
            "maxPrice": self.max_price,
            "priceCategory": self.price_category,
            "tripTag": self.trip_tag,
            "season": self.season,
        }
        for key, value in mapping.items():
            if value is not None:
                variables[key] = value
        return variables


class DestinationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination_name: str
    destination_country: str
    estimated_from_price_eur: float
    price_category: str
    trip_tags: str
    best_seasons: str
    description: Optional[str] = None


class AgentQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    limit: Optional[int] = Field(default=None, ge=1, le=10)
    chat_history: List[ChatMessage] = Field(default_factory=list)
    response_language: Optional[str] = None


class AgentQueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original_query: str
    applied_filters: DestinationFilters
    matched_terms: List[str]
    answer: str
    destinations: List[DestinationResult]


class ParsedQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: DestinationFilters
    matched_terms: List[str]
    region_constraint: Optional[str] = None


class LLMAvailability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool
    reason: Optional[str] = None
