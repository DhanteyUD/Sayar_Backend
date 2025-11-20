# from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from ..core.database import Base
#
#
# class Merchant(Base):
#     __tablename__ = "merchants"
#
#     id = Column(Integer, primary_key=True, index=True)
#     business_name = Column(String, index=True)
#     business_registration_number = Column(String, unique=True)
#     business_address = Column(String)
#     industry_type = Column(String)
#     business_category = Column(String)
#
#     # WhatsApp Integration
#     whatsapp_business_account_id = Column(String)
#     whatsapp_phone_number = Column(String)
#     whatsapp_access_token = Column(String)
#     whatsapp_verified = Column(Boolean, default=False)
#
#     # Meta Catalog Integration
#     meta_business_manager_id = Column(String)
#     meta_catalog_id = Column(String)
#
#     # Paystack Integration
#     paystack_subaccount_id = Column(String)
#     paystack_bank_code = Column(String)
#     paystack_account_number = Column(String)
#
#     # Status
#     onboarding_completed = Column(Boolean, default=False)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
#
#     # Foreign Keys
#     user_id = Column(Integer, ForeignKey("users.id"))
#
#     # Relationships
#     user = relationship("User", back_populates="merchant")
#     products = relationship("Product", back_populates="merchant")
#     orders = relationship("Order", back_populates="merchant")
