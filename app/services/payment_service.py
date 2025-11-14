import requests
from typing import Dict, Any, Optional
from ..core.config import settings


class PaystackService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = settings.PAYSTACK_BASE_URL

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def initialize_transaction(self, email: str, amount: float, reference: str,
                               metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Initialize a payment transaction"""
        url = f"{self.base_url}/transaction/initialize"
        payload = {
            "email": email,
            "amount": int(amount * 100),  # Convert to kobo
            "reference": reference,
            "metadata": metadata or {}
        }

        response = requests.post(url, json=payload, headers=self._get_headers())
        return response.json()

    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verify a transaction status"""
        url = f"{self.base_url}/transaction/verify/{reference}"
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def create_subaccount(self, business_name: str, account_number: str,
                          bank_code: str, percentage_charge: float = 1.0) -> Dict[str, Any]:
        """Create a subaccount for merchant"""
        url = f"{self.base_url}/subaccount"
        payload = {
            "business_name": business_name,
            "settlement_bank": bank_code,
            "account_number": account_number,
            "percentage_charge": percentage_charge,
            "primary_contact_email": f"{business_name.lower().replace(' ', '')}@sayar.com",
            "metadata": {"platform": "Sayar"}
        }

        response = requests.post(url, json=payload, headers=self._get_headers())
        return response.json()

    def create_transfer_recipient(self, name: str, account_number: str,
                                  bank_code: str) -> Dict[str, Any]:
        """Create transfer recipient for payouts"""
        url = f"{self.base_url}/transfer-recipient"
        payload = {
            "type": "nuban",
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": "NGN"
        }

        response = requests.post(url, json=payload, headers=self._get_headers())
        return response.json()


paystack_service = PaystackService()
