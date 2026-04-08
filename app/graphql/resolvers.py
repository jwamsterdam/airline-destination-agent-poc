from sqlalchemy.orm import Session

from app.db.models import Destination


def resolve_destinations(db: Session) -> list[Destination]:
    return db.query(Destination).all()
