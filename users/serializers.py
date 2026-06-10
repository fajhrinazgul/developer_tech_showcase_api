from rest_framework import serializers
from .models import User, Follow, EmailActivation
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import send_mail
from projects.models import Comment

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)
    following_count = serializers.IntegerField(source="following_set.count", read_only=True)
    projects_count = serializers.IntegerField(source="projects.count", read_only=True)
    total_comments_received = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "bio",
                  "avatar", "github_url", "linkedin_url", "website_url",
                  "followers_count", "following_count", "projects_count", "total_comments_received",
                  "date_joined"]
        read_only_fields = ["username", "email"]
    
    def get_total_comments_received(self, obj):
        count = 0
        projects = obj.projects.all()
        for project in projects:
            c = Comment.objects.filter(project=project).count()
            count += c
        return count


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "created_at"]
        read_only_fields = ["follower", "created_at"]
    
    def validate(self, data):
        # Mencegah user menfollow diri sendiri
        follower = self.context["request"].user
        following = data["following"]
        
        if follower == following:
            raise serializers.ValidationError(_("You do not follow yourself."))
        return data


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Tambahkan custom claims jika perlu
        token['username'] = user.username
        return token


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data, is_active=False)
        activation = EmailActivation.objects.create(user=user)
        
        activation_link = f"http://localhost:8000/api/activate/{activation.token}/"
        send_mail(
            "Aktifkan Akun Anda",
            f"Klik link berikut untuk mengaktifkan akun: {activation_link}",
            "no-reply@myapp.com",
            [user.email],
            fail_silently=False
        )
        return user