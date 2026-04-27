from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    """
    Backend ultra-robuste pour accepter e-mail ou téléphone.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # On essaie de récupérer l'identifiant peu importe le nom du champ (email, phone, username)
        identifier = username or kwargs.get('email') or kwargs.get('phone_number') or kwargs.get('username')
        
        if not identifier:
            return None
            
        try:
            # On cherche par e-mail ou par téléphone
            user = User.objects.get(Q(email=identifier) | Q(phone_number=identifier))
            
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        return None
