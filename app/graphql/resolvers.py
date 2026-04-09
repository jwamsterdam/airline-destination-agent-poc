from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Destination


def resolve_destinations(
    db: Session,
    country: str | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    price_category: str | None = None,
    trip_tag: str | None = None,
    season: str | None = None,
) -> list[Destination]:
    query = db.query(Destination)

    if country:
        query = query.filter(func.lower(Destination.destination_country) == country.lower())
    if min_price is not None:
        query = query.filter(Destination.estimated_from_price_eur >= min_price)
    if max_price is not None:
        query = query.filter(Destination.estimated_from_price_eur <= max_price)
    if price_category:
        query = query.filter(func.lower(Destination.price_category) == price_category.lower())
    if trip_tag:
        query = query.filter(Destination.trip_tags.ilike(f"%{trip_tag}%"))
    if season:
        query = query.filter(Destination.best_seasons.ilike(f"%{season}%"))

    return query.all()
