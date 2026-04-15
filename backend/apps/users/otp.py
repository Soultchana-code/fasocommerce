import random
import hashlib
import logging
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from celery import shared_task

logger = logging.getLogger('apps.users')


def generate_otp(length=6):
    """Génère un code OTP numérique."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def hash_otp(otp: str, phone_number: str) -> str:
    """Hash sécurisé du code OTP avec le numéro comme sel."""
    secret = f"{otp}:{phone_number}:{settings.SECRET_KEY}"
    return hashlib.sha256(secret.encode()).hexdigest()


def store_otp_in_cache(phone_number: str, otp: str, purpose: str) -> None:
    """Stocke l'OTP hashé dans Redis avec expiration."""
    key = f"{settings.OTP_CACHE_PREFIX}{purpose}:{phone_number}"
    hashed = hash_otp(otp, phone_number)
    cache.set(key, hashed, timeout=settings.OTP_EXPIRY_MINUTES * 60)


def verify_otp_from_cache(phone_number: str, otp: str, purpose: str) -> bool:
    """Vérifie un OTP depuis le cache Redis."""
    key = f"{settings.OTP_CACHE_PREFIX}{purpose}:{phone_number}"
    cached_hash = cache.get(key)
    if not cached_hash:
        return False
    submitted_hash = hash_otp(otp, phone_number)
    if cached_hash == submitted_hash:
        cache.delete(key)  # OTP à usage unique
        return True
    return False


@shared_task(name='users.send_sms_otp')
def send_sms_otp_task(phone_number: str, otp: str, purpose: str):
    """
    Tâche Celery pour l'envoi du SMS OTP.
    En production : intégrer le fournisseur SMS burkinabè (ex: Hub2, ARCEP BF).
    """
    logger.info(f"[OTP] Envoi code OTP [{purpose}] au {phone_number}")
    message = f"Votre code Faso-Commerce : {otp}. Valable {settings.OTP_EXPIRY_MINUTES} min. Ne le partagez pas."
    # TODO: Implémenter l'intégration SMS réelle
    # sms_provider.send(to=phone_number, message=message)
    logger.info(f"[OTP-SIM] Message envoyé à {phone_number}: {message}")
    return {'status': 'sent', 'phone': phone_number}
