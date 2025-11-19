import requests
from typing import Optional
from ..core.config import settings
from ..models.order import Order


class WhatsAppService:
    def __init__(self):
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def send_order_confirmation(self, whatsapp_id: str, order: Order):
        """Send order confirmation via WhatsApp"""
        if not self.access_token or not self.phone_number_id:
            return  # WhatsApp not configured

        message = {
            "messaging_product": "whatsapp",
            "to": whatsapp_id,
            "type": "template",
            "template": {
                "name": "order_confirmation",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": order.order_number},
                            {"type": "text", "text": f"₦{order.total_amount:,.2f}"},
                            {"type": "text", "text": order.customer_name}
                        ]
                    }
                ]
            }
        }

        try:
            response = requests.post(self.base_url, json=message, headers=self._get_headers())
            return response.json()
        except Exception as e:
            print(f"WhatsApp message failed: {e}")
            return None

    def send_text_message(self, whatsapp_id: str, message: str):
        """Send simple text message via WhatsApp"""
        if not self.access_token or not self.phone_number_id:
            return

        payload = {
            "messaging_product": "whatsapp",
            "to": whatsapp_id,
            "type": "text",
            "text": {"body": message}
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=self._get_headers())
            return response.json()
        except Exception as e:
            print(f"WhatsApp message failed: {e}")
            return None


whatsapp_service = WhatsAppService()
