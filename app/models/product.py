from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    currency = Column(String, default="NGN")
    sku = Column(String, unique=True)
    image_url = Column(String)
    cloudinary_public_id = Column(String)
    meta_product_id = Column(String)  # ID from Meta Catalog
    inventory_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    merchant_id = Column(Integer, ForeignKey("merchants.id"))

    # Relationships
    merchant = relationship("Merchant", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")