from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import AuthInfoView, GoogleLogin, CookieTokenObtainPairView, logout_user

urlpatterns = [
    path('auth/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("auth/logout/", logout_user, name="logout-user"),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("auth/me/", AuthInfoView.as_view(), name="auth-info"),
    path("auth/google/", GoogleLogin.as_view(), name="google-login"),
    path("auth/regitration/", include("dj_rest_auth.registration.urls")),
    # Tambahkan baris ini
    path('accounts/', include('allauth.urls')), 
    
    # API endpoints Anda yang lain
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
]