import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    print("Testing configuration loading...")
    print("-" * 50)

    from app.core.config import settings

    print("✅ Configuration loaded successfully!")
    print("-" * 50)
    print("\nConfiguration Values:")
    print(f"PROJECT_NAME: {settings.PROJECT_NAME}")
    print(f"VERSION: {settings.VERSION}")
    print(f"API_V1_STR: {settings.API_V1_STR}")
    print(f"APP_ENV: {settings.APP_ENV}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    print(f"SECRET_KEY: {'*' * 20} (hidden)")
    print(f"POSTGRES_USER: {settings.POSTGRES_USER}")
    print(f"POSTGRES_DB: {settings.POSTGRES_DB}")
    print(f"POSTGRES_SERVER: {settings.POSTGRES_SERVER}")
    print(f"POSTGRES_PORT: {settings.POSTGRES_PORT}")
    print(f"FIRST_ADMIN_EMAIL: {settings.FIRST_ADMIN_EMAIL}")

    print(f"\nCloudinary Configured: {bool(settings.CLOUDINARY_CLOUD_NAME)}")
    print(f"Paystack Configured: {bool(settings.PAYSTACK_SECRET_KEY)}")
    print(f"Twilio Configured: {bool(settings.TWILIO_ACCOUNT_SID)}")

    print("-" * 50)
    print("✅ All checks passed! Your configuration is ready.")

except Exception as e:
    print(f"❌ Error loading configuration: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
