from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Shipping(Base):
    __tablename__ = "shippings"

    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(String, unique=True, index=True)
    carrier = Column(String)  # dhl, fedex, ups, etc.
    status = Column(String, default="pending")  # pending, picked_up, in_transit, delivered
    shipping_address = Column(Text)
    estimated_delivery = Column(DateTime(timezone=True))
    actual_delivery = Column(DateTime(timezone=True))
    tracking_events = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    order_id = Column(Integer, ForeignKey("orders.id"))

    # Relationships
    order = relationship("Order", back_populates="shipping")