import strawberry

from app.graphql.resolvers import resolve_destinations


@strawberry.type
class DestinationType:
    id: int
    destination_iata: str
    destination_name: str
    destination_country: str
    estimated_from_price_eur: float
    price_category: str
    price_basis: str
    data_quality_note: str
    trip_tags: str
    best_seasons: str
    trip_lengths: str


@strawberry.type
class Query:
    @strawberry.field
    def destinations(self) -> list[DestinationType]:
        return list(resolve_destinations())


schema = strawberry.Schema(query=Query)
