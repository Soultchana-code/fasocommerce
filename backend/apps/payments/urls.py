from django.urls import path
from .views import (
    InitiatePaymentView,
    PaymentWebhookOrangeView,
    PaymentWebhookMoovView,
    PaymentListView,
    PaymentDetailView,
    PaymentAuditLogListView,
    VendorWalletView,
    WithdrawalRequestView,
)

urlpatterns = [
    # Paiements clients
    path('initiate/', InitiatePaymentView.as_view(), name='payment-initiate'),
    path('', PaymentListView.as_view(), name='payment-list'),
    path('<str:transaction_id>/', PaymentDetailView.as_view(), name='payment-detail'),
    # Webhooks opérateurs (pas d'auth — vérification par signature)
    path('webhook/orange/', PaymentWebhookOrangeView.as_view(), name='webhook-orange'),
    path('webhook/moov/', PaymentWebhookMoovView.as_view(), name='webhook-moov'),
    # Audit (admin)
    path('audit-logs/', PaymentAuditLogListView.as_view(), name='payment-audit-logs'),
    # Portefeuille vendeur
    path('wallet/', VendorWalletView.as_view(), name='vendor-wallet'),
    path('withdrawals/', WithdrawalRequestView.as_view(), name='withdrawal-list-create'),
]
