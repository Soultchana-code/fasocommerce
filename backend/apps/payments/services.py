import logging
import uuid
from django.conf import settings
from django.utils import timezone
import requests

logger = logging.getLogger('apps.payments')


class OrangeMoneyService:
    """
    Service d'intégration Orange Money Burkina Faso.
    Toutes les interactions sont tracées via PaymentAuditLog (exigence CDC).
    """
    BASE_URL = settings.ORANGE_MONEY_API_URL

    def __init__(self):
        self.api_key = settings.ORANGE_MONEY_API_KEY

    def initiate_payment(self, amount: float, phone: str, order_reference: str) -> dict:
        """Initie un paiement Orange Money."""
        payload = {
            'merchant_key': self.api_key,
            'currency': 'XOF',
            'order_id': order_reference,
            'amount': str(int(amount)),
            'return_url': f"{settings.FRONTEND_URL}/orders/{order_reference}/confirmation",
            'cancel_url': f"{settings.FRONTEND_URL}/orders/{order_reference}/cancel",
            'notif_url': f"{settings.BACKEND_URL}/api/v1/payments/webhook/orange/",
            'lang': 'fr',
            'reference': order_reference,
        }
        logger.info(f"[OrangeMoney] Initiation paiement — Ref: {order_reference}, Montant: {amount} XOF")
        try:
            response = requests.post(
                f"{self.BASE_URL}/webpayment",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=15
            )
            data = response.json()
            logger.info(f"[OrangeMoney] Réponse initiation — {data}")
            return {'success': True, 'data': data, 'raw': payload}
        except requests.RequestException as e:
            logger.error(f"[OrangeMoney] Erreur réseau — {e}")
            return {'success': False, 'error': str(e), 'raw': payload}

    def check_status(self, transaction_id: str) -> dict:
        """Vérifie le statut d'une transaction."""
        logger.info(f"[OrangeMoney] Vérification statut — TXN: {transaction_id}")
        try:
            response = requests.get(
                f"{self.BASE_URL}/transaction/{transaction_id}",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            data = response.json()
            logger.info(f"[OrangeMoney] Statut TXN {transaction_id} — {data}")
            return {'success': True, 'data': data}
        except requests.RequestException as e:
            logger.error(f"[OrangeMoney] Erreur vérification — {e}")
            return {'success': False, 'error': str(e)}


class MoovMoneyService:
    """
    Service d'intégration Moov Money (Flooz) Burkina Faso.
    """
    BASE_URL = settings.MOOV_MONEY_API_URL

    def __init__(self):
        self.api_key = settings.MOOV_MONEY_API_KEY

    def initiate_payment(self, amount: float, phone: str, order_reference: str) -> dict:
        payload = {
            'apiKey': self.api_key,
            'amount': int(amount),
            'subscriberMsisdn': phone,
            'reference': order_reference,
            'description': f'Commande Faso-Commerce {order_reference}',
        }
        logger.info(f"[MoovMoney] Initiation paiement — Ref: {order_reference}, Montant: {amount} XOF")
        try:
            response = requests.post(
                f"{self.BASE_URL}/cashIn",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=15
            )
            data = response.json()
            logger.info(f"[MoovMoney] Réponse — {data}")
            return {'success': True, 'data': data, 'raw': payload}
        except requests.RequestException as e:
            logger.error(f"[MoovMoney] Erreur réseau — {e}")
            return {'success': False, 'error': str(e), 'raw': payload}

    def check_status(self, transaction_id: str) -> dict:
        logger.info(f"[MoovMoney] Vérification statut — TXN: {transaction_id}")
        try:
            response = requests.get(
                f"{self.BASE_URL}/transaction/{transaction_id}",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            data = response.json()
            logger.info(f"[MoovMoney] Statut TXN {transaction_id} — {data}")
            return {'success': True, 'data': data}
        except requests.RequestException as e:
            logger.error(f"[MoovMoney] Erreur vérification — {e}")
            return {'success': False, 'error': str(e)}
