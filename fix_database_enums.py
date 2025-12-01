import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.core.database import engine


def fix_enum_types():
    """Drop and recreate enum types with correct values"""
    print("=" * 70)
    print("FIXING POSTGRESQL ENUM TYPES")
    print("=" * 70)

    with engine.connect() as conn:
        try:
            print("\n1️⃣  Dropping existing onboarding tables...")

            drop_tables = [
                "DROP TABLE IF EXISTS payment_configs CASCADE;",
                "DROP TABLE IF EXISTS catalog_configs CASCADE;",
                "DROP TABLE IF EXISTS whatsapp_configs CASCADE;",
                "DROP TABLE IF EXISTS merchant_onboarding CASCADE;"
            ]

            for sql in drop_tables:
                conn.execute(text(sql))
                print(f"   ✅ {sql}")

            print("\n2️⃣  Dropping old enum types...")

            drop_enums = [
                "DROP TYPE IF EXISTS onboardingstatus CASCADE;",
                "DROP TYPE IF EXISTS onboardingstepstatus CASCADE;",
                "DROP TYPE IF EXISTS businesscategory CASCADE;",
                "DROP TYPE IF EXISTS currency CASCADE;"
            ]

            for sql in drop_enums:
                conn.execute(text(sql))
                print(f"   ✅ {sql}")

            print("\n3️⃣  Creating new enum types with correct values...")

            create_enums = [
                "CREATE TYPE onboardingstatus AS ENUM ('not_started', 'in_progress', 'completed');",
                "CREATE TYPE onboardingstepstatus AS ENUM ('pending', 'completed', 'skipped');",
                """CREATE TYPE businesscategory AS ENUM (
                    'education', 'electronics', 'fashion', 'food_beverage',
                    'health_beauty', 'home_garden', 'retail', 'services',
                    'sports_fitness', 'wholesale', 'other'
                );""",
                "CREATE TYPE currency AS ENUM ('NGN', 'USD', 'GBP', 'EUR');"
            ]

            for sql in create_enums:
                conn.execute(text(sql))
                print(f"   ✅ Created enum type")

            conn.commit()

            print("\n4️⃣  Recreating tables...")

            from app.models import onboarding
            from app.core.database import Base

            Base.metadata.create_all(bind=engine)

            print("   ✅ All tables recreated successfully!")

            print("\n" + "=" * 70)
            print("✅ SUCCESS! Enum types fixed!")
            print("=" * 70)
            print("\nYou can now:")
            print("1. Restart your application")
            print("2. Test the onboarding endpoints")
            print("\nTry: GET /api/v1/onboarding/progress?merchant_id=YOUR_MERCHANT_ID")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            conn.rollback()
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will drop all onboarding-related tables!")
    print("   All onboarding progress will be lost.")
    response = input("\nDo you want to continue? (yes/no): ").strip().lower()

    if response == "yes":
        fix_enum_types()
    else:
        print("\n❌ Cancelled. No changes made.")
