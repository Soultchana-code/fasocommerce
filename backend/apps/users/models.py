from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
import string


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Le numéro de téléphone est obligatoire.")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        VENDOR = 'vendor', 'Vendeur'
        ADMIN = 'admin', 'Administrateur'

    phone_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de téléphone")
    email = models.EmailField(blank=True, null=True, unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Nom")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT, verbose_name="Rôle")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")

    # Localisation (adressage alternatif BF)
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    district = models.CharField(max_length=100, blank=True, verbose_name="Quartier")
    landmark = models.CharField(max_length=255, blank=True, verbose_name="Repère géographique")

    # MFA
    is_phone_verified = models.BooleanField(default=False, verbose_name="Téléphone vérifié")
    mfa_enabled = models.BooleanField(default=True, verbose_name="MFA activé")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.phone_number


class OTPLog(models.Model):
    """Traçabilité des OTP envoyés — requis par le cahier des charges (audit)."""
    class Purpose(models.TextChoices):
        REGISTRATION = 'registration', 'Inscription'
        LOGIN = 'login', 'Connexion'
        PAYMENT = 'payment', 'Paiement'
        PASSWORD_RESET = 'password_reset', 'Réinitialisation'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_logs')
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    code_hash = models.CharField(max_length=128)  # On stocke le hash, jamais le code brut
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'otp_logs'
        verbose_name = 'Journal OTP'
        verbose_name_plural = 'Journaux OTP'
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP [{self.purpose}] - {self.user.phone_number} - {self.created_at}"
