from rest_framework import serializers
from .models import Payment, PaymentAuditLog, VendorWallet, WithdrawalRequest


class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    provider = serializers.ChoiceField(choices=Payment.Provider.choices)
    phone_number = serializers.CharField(max_length=20)


class PaymentSerializer(serializers.ModelSerializer):
    order_reference = serializers.CharField(source='order.reference', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'external_reference',
            'order_reference', 'provider', 'provider_display',
            'amount', 'currency', 'phone_number',
            'status', 'status_display', 'status_message',
            'created_at', 'confirmed_at',
        ]
        read_only_fields = fields


class PaymentAuditLogSerializer(serializers.ModelSerializer):
    transaction_id = serializers.CharField(source='payment.transaction_id', read_only=True)

    class Meta:
        model = PaymentAuditLog
        fields = ['id', 'transaction_id', 'event', 'old_status', 'new_status', 'payload', 'actor_ip', 'created_at']


class VendorWalletSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    vendor_phone = serializers.CharField(source='vendor.phone_number', read_only=True)

    class Meta:
        model = VendorWallet
        fields = ['id', 'vendor_name', 'vendor_phone', 'balance', 'total_earned', 'total_withdrawn', 'updated_at']
        read_only_fields = fields


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ['id', 'amount', 'phone_number', 'provider', 'status', 'notes', 'created_at', 'processed_at']
        read_only_fields = ['status', 'created_at', 'processed_at']

    def validate_amount(self, value):
        wallet = self.context['request'].user.wallet
        if value > wallet.balance:
            raise serializers.ValidationError(
                f"Solde insuffisant. Votre solde est de {wallet.balance} FCFA."
            )
        if value < 1000:
            raise serializers.ValidationError("Le montant minimum de retrait est de 1 000 FCFA.")
        return value

    def create(self, validated_data):
        validated_data['wallet'] = self.context['request'].user.wallet
        return super().create(validated_data)
