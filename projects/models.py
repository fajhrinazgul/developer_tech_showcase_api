import os
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_delete

User = get_user_model()


class Technology(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name


class ProjectManager(models.Manager):
    def published(self):
        return self.filter(is_published=True)
    
    def by_user(self, username):
        return self.filter(author__username=username, is_published=True)


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects",
                               verbose_name=_("author"))
    title = models.CharField(_("title"), max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    description = models.TextField(_("description"), help_text=_("Description project with markdown format."))
    thumbnail = models.ImageField(upload_to="projects/thumbnails/", blank=True, null=True)
    demo_url = models.URLField(blank=True, null=True)
    source_code_url = models.URLField(blank=True, null=True)
    tech_stack = models.ManyToManyField(Technology, related_name="projects", blank=True)
    is_published = models.BooleanField(default=False)
    view_count = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProjectManager()
    
    class Meta:
        ordering = ["-created_at"]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(self.id)[:8]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"


class Like(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Bookmark(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ("user", "project")
    
    def __str__(self):
        return f"{self.user.username} saved {self.project.title}"


class ProjectView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Menjamin satu user hanya bisa punya satu record view untuk satu project
        unique_together = ('user', 'project')


@receiver(post_delete, sender=Project)
def auto_delete_image_on_delete_project(sender, instance, **kwargs):
    image = instance.thumbnail
    if image:
        if os.path.isfile(image.path):
            os.remove(image.path)