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
                        destination_iata=row["destination_iata"],
                        destination_name=row["destination_name"],
                        destination_country=row["destination_country"],
                        estimated_from_price_eur=float(row["estimated_from_price_eur"]),
                        price_category=row["price_category"],
                        price_basis=row["price_basis"],
                        data_quality_note=row["data_quality_note"],
                        trip_tags=row["trip_tags"],
                        best_seasons=row["best_seasons"],
                        trip_lengths=row["trip_lengths"],
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
