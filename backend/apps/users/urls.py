from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    OTPRequestView,
    OTPVerifyView,
    UserProfileView,
    UserListView,
    OTPLogListView,
)

urlpatterns = [
    # Authentification
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # OTP / MFA
    path('otp/request/', OTPRequestView.as_view(), name='otp-request'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    # Profil
    path('me/', UserProfileView.as_view(), name='user-profile'),
    # Admin
    path('', UserListView.as_view(), name='user-list'),
    path('otp-logs/', OTPLogListView.as_view(), name='otp-log-list'),
]
