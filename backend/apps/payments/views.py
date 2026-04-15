import logging
from django.utils import timezone
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Payment, PaymentAuditLog, VendorWallet, WithdrawalRequest
from .serializers import (
    InitiatePaymentSerializer, PaymentSerializer,
    PaymentAuditLogSerializer, VendorWalletSerializer,
    WithdrawalRequestSerializer,
)
from .services import OrangeMoneyService, MoovMoneyService
from apps.orders.models import Order
from apps.users.models import User

logger = logging.getLogger('apps.payments')


def log_payment_event(payment, event, old_status='', new_status='', payload=None, ip=None):
    """Helper : crée une entrée dans le journal d'audit — exigence CDC."""
    PaymentAuditLog.objects.create(
        payment=payment,
        event=event,
        old_status=old_status,
        new_status=new_status,
        payload=payload or {},
        actor_ip=ip,
    )


class InitiatePaymentView(APIView):
    """
    Initier un paiement Mobile Money.
    Supporte Orange Money et Moov Money (Flooz).
    Toutes les interactions sont journalisées.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Payments'], request=InitiatePaymentSerializer)
    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = Order.objects.get(pk=data['order_id'], client=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Commande introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != Order.Status.PENDING:
            return Response({'error': 'Cette commande n\'est pas en attente de paiement.'}, status=status.HTTP_400_BAD_REQUEST)

        provider = data['provider']
        phone = data['phone_number']

        # Sélectionner le bon service
        service = OrangeMoneyService() if provider == Payment.Provider.ORANGE_MONEY else MoovMoneyService()

        # Créer l'objet Payment
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            provider=provider,
            amount=order.total_amount,
            phone_number=phone,
            status=Payment.Status.INITIATED,
        )

        # Appel API opérateur
        result = service.initiate_payment(float(order.total_amount), phone, order.reference)

        # Mettre à jour et journaliser
        payment.raw_request = result.get('raw', {})
        payment.raw_response = result.get('data', {})

        if result['success']:
            payment.status = Payment.Status.PENDING
            payment.external_reference = result['data'].get('pay_token') or result['data'].get('reference', '')
            payment.save()
            log_payment_event(
                payment, 'PAYMENT_INITIATED',
                old_status=Payment.Status.INITIATED,
                new_status=Payment.Status.PENDING,
                payload=result.get('data', {}),
                ip=get_client_ip(request),
            )
            return Response({
                'message': 'Paiement initié. Confirmez sur votre téléphone.',
                'transaction_id': payment.transaction_id,
                'payment_url': result['data'].get('payment_url', ''),
                'status': payment.status,
            }, status=status.HTTP_201_CREATED)
        else:
            payment.status = Payment.Status.FAILED
            payment.status_message = result.get('error', 'Erreur inconnue')
            payment.save()
            log_payment_event(
                payment, 'PAYMENT_FAILED',
                old_status=Payment.Status.INITIATED,
                new_status=Payment.Status.FAILED,
                payload={'error': result.get('error')},
                ip=get_client_ip(request),
            )
            return Response({'error': 'Échec de l\'initiation du paiement. Réessayez.'}, status=status.HTTP_502_BAD_GATEWAY)


class PaymentWebhookOrangeView(APIView):
    """Webhook de confirmation Orange Money."""
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=['Payments'])
    def post(self, request):
        payload = request.data
        logger.info(f"[OrangeMoney Webhook] Payload reçu: {payload}")
        txn_id = payload.get('txnid') or payload.get('transaction_id')
        new_status_raw = payload.get('status', '').lower()

        try:
            payment = Payment.objects.get(external_reference=txn_id)
        except Payment.DoesNotExist:
            logger.warning(f"[OrangeMoney Webhook] Paiement introuvable pour txnid={txn_id}")
            return Response({'status': 'ignored'})

        old_status = payment.status
        payment.webhook_payload = payload
        if new_status_raw in ['successfull', 'success', '200']:
            payment.status = Payment.Status.SUCCESS
            payment.confirmed_at = timezone.now()
            payment.order.status = Order.Status.PAID
            payment.order.save(update_fields=['status'])
        elif new_status_raw in ['failed', 'error']:
            payment.status = Payment.Status.FAILED
        payment.save()

        log_payment_event(
            payment, 'WEBHOOK_ORANGE',
            old_status=old_status,
            new_status=payment.status,
            payload=payload,
        )
        return Response({'status': 'processed'})


class PaymentWebhookMoovView(APIView):
    """Webhook de confirmation Moov Money."""
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=['Payments'])
    def post(self, request):
        payload = request.data
        logger.info(f"[MoovMoney Webhook] Payload reçu: {payload}")
        txn_id = payload.get('referenceId') or payload.get('transactionId')

        try:
            payment = Payment.objects.get(external_reference=txn_id)
        except Payment.DoesNotExist:
            logger.warning(f"[MoovMoney Webhook] Paiement introuvable pour txnid={txn_id}")
            return Response({'status': 'ignored'})

        old_status = payment.status
        payment.webhook_payload = payload
        result_code = payload.get('resultCode', '')
        if result_code == '0' or payload.get('status') == 'SUCCESS':
            payment.status = Payment.Status.SUCCESS
            payment.confirmed_at = timezone.now()
            payment.order.status = Order.Status.PAID
            payment.order.save(update_fields=['status'])
        else:
            payment.status = Payment.Status.FAILED
        payment.save()

        log_payment_event(
            payment, 'WEBHOOK_MOOV',
            old_status=old_status,
            new_status=payment.status,
            payload=payload,
        )
        return Response({'status': 'processed'})


class PaymentListView(generics.ListAPIView):
    """Liste des paiements de l'utilisateur connecté."""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Payments'])
    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return Payment.objects.select_related('order', 'user').all()
        return Payment.objects.filter(user=user).select_related('order')


class PaymentDetailView(generics.RetrieveAPIView):
    """Détail d'un paiement."""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_id'

    @extend_schema(tags=['Payments'])
    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)


class PaymentAuditLogListView(generics.ListAPIView):
    """Journal d'audit des paiements — Admins uniquement."""
    serializer_class = PaymentAuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(tags=['Admin'])
    def get_queryset(self):
        qs = PaymentAuditLog.objects.select_related('payment')
        txn = self.request.query_params.get('transaction_id')
        if txn:
            qs = qs.filter(payment__transaction_id=txn)
        return qs.order_by('-created_at')


class VendorWalletView(generics.RetrieveAPIView):
    """Solde du portefeuille vendeur."""
    serializer_class = VendorWalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Payments'])
    def get_object(self):
        wallet, _ = VendorWallet.objects.get_or_create(vendor=self.request.user)
        return wallet


class WithdrawalRequestView(generics.ListCreateAPIView):
    """Demandes de retrait vendeur."""
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Payments'])
    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return WithdrawalRequest.objects.select_related('wallet__vendor').all()
        wallet, _ = VendorWallet.objects.get_or_create(vendor=user)
        return WithdrawalRequest.objects.filter(wallet=wallet)


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')
