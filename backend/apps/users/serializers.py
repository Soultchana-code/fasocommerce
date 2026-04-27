from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, OTPLog


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'first_name', 'last_name',
            'role', 'city', 'district', 'landmark',
            'password', 'password_confirm',
        ]
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True},
            'phone_number': {'required': True},
            'role': {'default': User.Role.CLIENT},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        # Seuls les admins peuvent créer des vendeurs/admins via cette route
        request = self.context.get('request')
        if data.get('role') in [User.Role.VENDOR, User.Role.ADMIN]:
            if not request or not request.user.is_authenticated or request.user.role != User.Role.ADMIN:
                raise serializers.ValidationError({"role": "Vous n'êtes pas autorisé à créer ce type de compte."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Bypass cache navigateur : si l'email est manquant, on en génère un
        if not validated_data.get('email'):
            phone = validated_data.get('phone_number')
            # Nettoyage du numéro pour l'email
            clean_phone = "".join(filter(str.isdigit, phone))
            validated_data['email'] = f"user_{clean_phone}@fasocommerce.bf"
            
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'avatar', 'city', 'district', 'landmark',
            'is_phone_verified', 'mfa_enabled', 'date_joined',
        ]
        read_only_fields = ['id', 'phone_number', 'role', 'is_phone_verified', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name()


class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    purpose = serializers.ChoiceField(choices=OTPLog.Purpose.choices)


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    otp_code = serializers.CharField(max_length=6, min_length=6)
    purpose = serializers.ChoiceField(choices=OTPLog.Purpose.choices)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On rend le champ identifiant (email) optionnel pour permettre phone_number à la place
        self.fields[self.username_field].required = False

    # On ajoute aussi phone_number explicitement
    phone_number = serializers.CharField(required=False)

    def validate(self, attrs):
        # On récupère l'identifiant peu importe le nom
        identifier = attrs.get("email") or attrs.get("phone_number") or attrs.get("username")
        if identifier:
            attrs[self.username_field] = identifier
        
        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['phone'] = user.phone_number
        token['full_name'] = user.get_full_name()
        return token


class OTPLogSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = OTPLog
        fields = ['id', 'user_phone', 'purpose', 'is_used', 'created_at', 'used_at', 'ip_address']
