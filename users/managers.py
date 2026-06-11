from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _ 
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(first_name=first_name, last_name=last_name, username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, first_name, last_name, username, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(first_name, last_name, username, email, password, **extra_fields)
    
    def get_with_profile(self, username):
        # Mengambil user beserta relasi penting agar tidak terjadi N+1 query
        return self.get_queryset().prefetch_related('following', 'followers').get(username=username)

    def get_top_creators(self):
        # Ide: Mendapatkan user dengan follower terbanyak (untuk section 'Recommended to Follow')
        return self.annotate(followers_count=models.Count('followers')).order_by('-followers_count')
    

class FollowManager(models.Manager):
    def is_following(self, follower, following):
        """Mengecek apakah user A sudah mengikuti user B

        Args:
            username (_type_): _description_
        """
        return self.filter(follower=follower, following=following).exists()
    
    def toggle_follow(self, follower, following):
        """Logika: jika sudah follow, maka unfollow, jika belum maka follow
        """
        instance = self.filter(follower=follower, following=following)
        if instance.exists():
            instance.delete()
            return False
        else:
            self.create(follower=follower, following=following)
            return True