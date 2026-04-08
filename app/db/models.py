from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Destination(Base):
    """Destination row mapped from the PoC Transavia dataset."""

    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Location identifiers
    destination_iata: Mapped[str] = mapped_column(String(8), index=True)
    destination_name: Mapped[str] = mapped_column(String(255), index=True)
    destination_country: Mapped[str] = mapped_column(String(128), index=True)

    # Commercial pricing fields (synthetic PoC data)
    estimated_from_price_eur: Mapped[float] = mapped_column(Float, index=True)
    price_category: Mapped[str] = mapped_column(String(64), index=True)
    price_basis: Mapped[str] = mapped_column(String(255))
    data_quality_note: Mapped[str] = mapped_column(Text)

    # Agent-friendly filtering fields (stored as comma-separated text)
    trip_tags: Mapped[str] = mapped_column(Text)
    best_seasons: Mapped[str] = mapped_column(Text)
    trip_lengths: Mapped[str] = mapped_column(Text)
