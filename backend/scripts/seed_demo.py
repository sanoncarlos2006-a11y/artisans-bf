from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import SessionLocal, init_db
from app.services.demo_seed import DEMO_OWNER, seed_demo_data


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        result = seed_demo_data(db)
    finally:
        db.close()

    print("Demo database seeded successfully.")
    print("Demo owner:")
    print(f"  phone: {DEMO_OWNER['phone']}")
    print(f"  email: {DEMO_OWNER['email']}")
    print(f"  password: {DEMO_OWNER['password']}")
    print("Demo businesses:")
    for business in result.businesses:
        print(f"  - {business.name} [{business.category}] status={business.status}")


if __name__ == "__main__":
    main()
