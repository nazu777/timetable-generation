"""Demo seeder — run: python -m app.seed_demo"""
from app.core.database import SessionLocal


def main() -> None:
    print("Seeding demo data... (plug real entities here)")
    db = SessionLocal()
    db.close()
    print("Done.")


if __name__ == "__main__":
    main()
