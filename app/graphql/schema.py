from typing import Optional

import strawberry

from app.db.models import Destination
from app.db.session import SessionLocal
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
    def destinations(
        self,
        country: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        price_category: Optional[str] = None,
        trip_tag: Optional[str] = None,
        season: Optional[str] = None,
    ) -> list[DestinationType]:
        db = SessionLocal()
        try:
            destinations = resolve_destinations(
                db,
                country=country,
                max_price=max_price,
                min_price=min_price,
                price_category=price_category,
                trip_tag=trip_tag,
                season=season,
            )
            return [map_destination_to_graphql(destination) for destination in destinations]
        finally:
            db.close()


def map_destination_to_graphql(destination: Destination) -> DestinationType:
    return DestinationType(
        id=destination.id,
        destination_iata=destination.destination_iata,
        destination_name=destination.destination_name,
        destination_country=destination.destination_country,
        estimated_from_price_eur=destination.estimated_from_price_eur,
        price_category=destination.price_category,
        price_basis=destination.price_basis,
        data_quality_note=destination.data_quality_note,
        trip_tags=destination.trip_tags,
        best_seasons=destination.best_seasons,
        trip_lengths=destination.trip_lengths,
    )


schema = strawberry.Schema(query=Query)
