from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import os, uuid

from .managers import UserManager, FollowManager

def get_avatar_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    username = str(instance.username)
    uid = str(uuid.uuid4())
    return os.path.join("avatars", username, uid + ext)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_("first name"), max_length=50)
    last_name = models.CharField(_("last name"), max_length=50)
    username = models.CharField(unique=True, max_length=30)
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to=get_avatar_path, blank=True)
    following = models.ManyToManyField("self", through="Follow", symmetrical=False,
                                       related_name="followers")
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]
    
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj = ...):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser

class Follow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_set")
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = FollowManager()
    
    class Meta:
        unique_together = ("follower", "following")
    
    def __str__(self):
        return f"{self.follower.username} => {self.following.username}"


class EmailActivation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    