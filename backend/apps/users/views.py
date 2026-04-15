import logging
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import OTPLog
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    CustomTokenObtainPairSerializer,
    OTPLogSerializer,
)
from .otp import generate_otp, store_otp_in_cache, verify_otp_from_cache, hash_otp, send_sms_otp_task

User = get_user_model()
logger = logging.getLogger('apps.users')


class RegisterView(generics.CreateAPIView):
    """Inscription d'un nouvel utilisateur."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=['Auth'])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Envoyer OTP de vérification
        otp = generate_otp()
        store_otp_in_cache(user.phone_number, otp, OTPLog.Purpose.REGISTRATION)
        send_sms_otp_task.delay(user.phone_number, otp, OTPLog.Purpose.REGISTRATION)
        OTPLog.objects.create(
            user=user,
            purpose=OTPLog.Purpose.REGISTRATION,
            code_hash=hash_otp(otp, user.phone_number),
            ip_address=get_client_ip(request),
        )
        return Response(
            {'message': 'Inscription réussie. Un code OTP a été envoyé par SMS.', 'phone_number': user.phone_number},
            status=status.HTTP_201_CREATED
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Connexion avec numéro de téléphone + mot de passe."""
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(tags=['Auth'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class OTPRequestView(APIView):
    """Demander l'envoi d'un OTP par SMS."""
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=['Auth'], request=OTPRequestSerializer)
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        purpose = serializer.validated_data['purpose']
        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            # Ne pas révéler si le numéro existe (sécurité)
            return Response({'message': 'Si ce numéro est enregistré, un SMS vous a été envoyé.'})
        otp = generate_otp()
        store_otp_in_cache(phone, otp, purpose)
        send_sms_otp_task.delay(phone, otp, purpose)
        OTPLog.objects.create(
            user=user,
            purpose=purpose,
            code_hash=hash_otp(otp, phone),
            ip_address=get_client_ip(request),
        )
        logger.info(f"OTP [{purpose}] demandé pour {phone}")
        return Response({'message': 'Code OTP envoyé par SMS.'})


class OTPVerifyView(APIView):
    """Vérifier un code OTP reçu par SMS."""
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=['Auth'], request=OTPVerifySerializer)
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']
        purpose = serializer.validated_data['purpose']

        is_valid = verify_otp_from_cache(phone, otp_code, purpose)
        if not is_valid:
            return Response({'error': 'Code OTP invalide ou expiré.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        # Marquer l'OTP comme utilisé
        OTPLog.objects.filter(user=user, purpose=purpose, is_used=False).update(
            is_used=True, used_at=timezone.now()
        )

        if purpose == OTPLog.Purpose.REGISTRATION:
            user.is_phone_verified = True
            user.save(update_fields=['is_phone_verified'])

        # Si vérification de transaction, retourner les tokens
        if purpose == OTPLog.Purpose.LOGIN:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'role': user.role,
            })

        return Response({'message': 'Code OTP validé avec succès.', 'purpose': purpose})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Consulter et mettre à jour son profil."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Users'])
    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """Liste des utilisateurs — Admins uniquement."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(tags=['Users'])
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')


class OTPLogListView(generics.ListAPIView):
    """
    Historique des OTP pour audit.
    Accessible aux admins uniquement — Exigence traçabilité du CDC.
    """
    serializer_class = OTPLogSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(tags=['Admin'])
    def get_queryset(self):
        return OTPLog.objects.select_related('user').order_by('-created_at')


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')
