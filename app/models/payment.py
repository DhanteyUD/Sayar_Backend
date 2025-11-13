from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    paystack_reference = Column(String, unique=True, index=True)
    paystack_transaction_id = Column(String)
    amount = Column(Float)
    currency = Column(String, default="NGN")
    status = Column(String)  # pending, success, failed
    payment_method = Column(String)
    paystack_response = Column(JSON)  # Full Paystack response
    paid_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Foreign Keys
    order_id = Column(Integer, ForeignKey("orders.id"))

    # Relationships
    order = relationship("Order", back_populates="payment")