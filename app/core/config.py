# from pydantic_settings import BaseSettings
# from typing import Optional
#
# class Settings(BaseSettings):
#     # Database
#     DATABASE_URL: str = "postgresql://sayar_user:password@localhost:5432/sayar_db"
#
#     # JWT
#     SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
#     REFRESH_TOKEN_EXPIRE_DAYS: int = 7
#
#     # Paystack
#     PAYSTACK_PUBLIC_KEY: str = "pk_test_paystack_public_key"
#     PAYSTACK_SECRET_KEY: str = "sk_test_paystack_secret_key"
#     PAYSTACK_BASE_URL: str = "https://api.paystack.co"
#
#     # Cloudinary
#     CLOUDINARY_CLOUD_NAME: str = "demo"
#     CLOUDINARY_API_KEY: str = "demo_key"
#     CLOUDINARY_API_SECRET: str = "demo_secret"
#
#     # WhatsApp
#     WHATSAPP_ACCESS_TOKEN: Optional[str] = None
#     WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
#
#     class Config:
#         env_file = ".env"
#         case_sensitive = True
#
#
# settings = Settings()