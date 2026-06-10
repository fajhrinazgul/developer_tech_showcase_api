import os
from dotenv import load_dotenv
load_dotenv()
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.utils.translation import gettext as _
from dj_rest_auth.registration.views import SocialLoginView, RegisterView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from rest_framework_simplejwt.views import TokenObtainPairView


from .models import  User, Follow, EmailActivation
from .serializers import UserSerializer, FollowSerializer, RegisterSerializer
from .permissions import IsOwnerOrAdminOrReadOnly

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    lookup_field = "username"


class FollowToggleSerializer(APIView):
    """Class for implement toggle follow view
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)
        this_user = request.user
        
        if this_user == target_user:
            return Response({"status": "error", "message": "You do not follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        is_following = Follow.objects.toggle_follow(this_user, target_user)
        
        message = _("Successfully followed") if is_following else _("Successfully unfollow")
        return Response({"status": "success", "message": message, "is_following": is_following})


class UserFollowersView(generics.ListAPIView):
    serializer_class = UserSerializer
    
    def get_queryset(self):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        return user.followers.all()
    

class UserFollowingView(generics.ListAPIView):
    serializer_class = UserSerializer
    
    def get_queryset(self):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        return user.following.all()


class AuthInfoView(APIView):
    # Hanya user yang memiliki token valid yang bisa akses
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # request.user secara otomatis terisi oleh SimpleJWT berdasarkan token
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    
"""
Email activation / REGISTER
"""

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "message": "User berhasil terdaftar. Silahkan cek email Anda untuk aktifasi."
        }, status=status.HTTP_201_CREATED)


class ActivateAccountView(APIView):
    def get(self, request, token):
        activation = get_object_or_404(EmailActivation, token=token)
        user = activation.user
        user.is_active = True
        user.save()
        activation.delete()
        return Response({"status": "success", "message": "Akun berhasil diaktifkan"})

class CheckAvailabilityView(APIView):
    def get(self, request):
        field = request.query_params.get('field') # 'username' atau 'email'
        value = request.query_params.get('value')
        
        if not field or not value or field not in ['username', 'email']:
            return Response({"error": "Invalid field"}, status=400)
            
        exists = User.objects.filter(**{field: value}).exists()
        return Response({"available": not exists})


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = os.getenv("LOGIN_CALLBACK_URL")
    client_class = OAuth2Client
    
    def post(self, request, *args, **kwargs):
        # 1. Panggil logika login asli (memverifikasi token Google)
        response = super().post(request, *args, **kwargs)
        
        # 2. Cek apakah login berhasil (response status 200)
        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            print(response.data)
            print(access_token)
            # 3. Set Access Token ke Cookie
            if access_token:
                response.set_cookie(
                    key="access_token",
                    value=refresh_token,
                    httponly=True,
                    secure=False,
                    samesite='Lax',
                    path="/",
                    max_age=3600 * 24 * 7,
                )

            # 4. Set Refresh Token ke Cookie
            if refresh_token:
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=False,
                    samesite='Lax',
                    path="/",
                    max_age=3600 * 24 * 7,
                )
            
        return response



class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        access_token = response.data.get("access")
        refresh_token = response.data.get("refresh")
        
        if access_token:
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                path="/",
                max_age=3600 * 24 * 7,
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                path="/",
                max_age=3600 * 24 * 7,
            )
        return response


def logout_user(request):
    response = Response({"message": "Logout successful"})
    response.delete_cookie("token")
    response.delete_cookie("refresh")
    return response