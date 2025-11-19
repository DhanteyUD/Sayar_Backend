import uuid
from datetime import datetime


def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"ORD{timestamp}{unique_id}"


def format_currency(amount: float, currency: str = "NGN") -> str:
    """Format currency for display"""
    if currency == "NGN":
        return f"₦{amount:,.2f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def validate_phone_number(phone: str) -> bool:
    """Basic phone number validation"""
    # Remove any non-digit characters
    cleaned = ''.join(filter(str.isdigit, phone))
    return len(cleaned) >= 10
