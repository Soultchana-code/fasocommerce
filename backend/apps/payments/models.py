import uuid
import logging
import hashlib
import hmac
from django.db import models
from apps.users.models import User
from apps.orders.models import Order

logger = logging.getLogger('apps.payments')


class Payment(models.Model):
    class Provider(models.TextChoices):
        ORANGE_MONEY = 'orange_money', 'Orange Money'
        MOOV_MONEY = 'moov_money', 'Moov Money'

    class Status(models.TextChoices):
        INITIATED = 'initiated', 'Initié'
        PENDING = 'pending', 'En attente de confirmation'
        SUCCESS = 'success', 'Réussi'
        FAILED = 'failed', 'Échoué'
        CANCELLED = 'cancelled', 'Annulé'
        REFUNDED = 'refunded', 'Remboursé'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=20, choices=Provider.choices, verbose_name="Opérateur")
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Montant (FCFA)")
    currency = models.CharField(max_length=5, default='XOF', verbose_name="Devise")

    # Identifiants externes
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name="ID Transaction")
    external_reference = models.CharField(max_length=100, blank=True, verbose_name="Référence opérateur")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro payeur")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    status_message = models.TextField(blank=True, verbose_name="Message statut opérateur")

    # Traçabilité exhaustive — Exigence CDC section 3.2
    raw_request = models.JSONField(default=dict, verbose_name="Requête brute envoyée")
    raw_response = models.JSONField(default=dict, verbose_name="Réponse brute reçue")
    webhook_payload = models.JSONField(null=True, blank=True, verbose_name="Payload webhook reçu")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['provider', 'status']),
        ]

    def __str__(self):
        return f"[{self.provider}] {self.amount} FCFA — {self.status} ({self.transaction_id})"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class PaymentAuditLog(models.Model):
    """
    Journal d'audit immuable des interactions avec les APIs de paiement.
    Exigence explicite du Cahier des Charges (section 3.2 Traçabilité).
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='audit_logs')
    event = models.CharField(max_length=100, verbose_name="Événement")
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    payload = models.JSONField(default=dict, verbose_name="Données de l'événement")
    actor_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_audit_logs'
        verbose_name = 'Journal audit paiement'
        verbose_name_plural = 'Journaux audit paiements'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.event}] {self.payment.transaction_id} — {self.created_at}"


class VendorWallet(models.Model):
    """Portefeuille vendeur pour le suivi des fonds et retraits."""
    vendor = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='wallet',
        limit_choices_to={'role': 'vendor'}
    )
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Solde (FCFA)")
    total_earned = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Total gagné (FCFA)")
    total_withdrawn = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Total retiré (FCFA)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_wallets'
        verbose_name = 'Portefeuille vendeur'

    def __str__(self):
        return f"Portefeuille {self.vendor.phone_number} — {self.balance} FCFA"


class WithdrawalRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        APPROVED = 'approved', 'Approuvé'
        REJECTED = 'rejected', 'Rejeté'
        PAID = 'paid', 'Payé'

    wallet = models.ForeignKey(VendorWallet, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Montant demandé (FCFA)")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro Mobile Money")
    provider = models.CharField(max_length=20, choices=Payment.Provider.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    processed_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='processed_withdrawals'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'withdrawal_requests'
        verbose_name = 'Demande de retrait'

    def __str__(self):
        return f"Retrait {self.amount} FCFA — {self.wallet.vendor.phone_number} [{self.status}]"
