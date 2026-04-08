import csv
from pathlib import Path

from app.db.models import Destination
from app.db.session import Base, SessionLocal, engine

DEFAULT_CSV_PATH = Path("app/data/raw/transavia_destinations_cleaned_for_poc.csv")


def load_destinations(csv_path: Path = DEFAULT_CSV_PATH) -> int:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        session.query(Destination).delete()

        with csv_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            rows = []
            for row in reader:
                rows.append(
                    Destination(
                        destination_iata=row.get("destination_code") or "",
                        destination_name=row.get("destination") or "",
                        destination_country=row.get("country") or "",
                        estimated_from_price_eur=float(row.get("estimated_from_price_eur") or 0),
                        price_category=row.get("price_category") or "",
                        price_basis=row.get("price_basis") or "",
                        data_quality_note=row.get("data_quality_note") or "",
                        trip_tags=row.get("trip_tags") or "",
                        best_seasons=row.get("best_seasons") or "",
                        trip_lengths=row.get("trip_lengths") or "",
                    )
                )

        session.bulk_save_objects(rows)
        session.commit()
        return len(rows)
    finally:
        session.close()


if __name__ == "__main__":
    inserted_count = load_destinations()
    print(f"Inserted {inserted_count} destinations.")
