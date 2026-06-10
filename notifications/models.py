from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from projects.models import Project, Like, Comment
import uuid

User = get_user_model()


class Notification(models.Model):
    ACTION_LIKE = 'like'
    ACTION_COMMENT = 'comment'
    ACTION_CHOICES = [(ACTION_LIKE, 'Like'), (ACTION_COMMENT, 'Comment')]
    
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications", null=True)
    message = models.CharField(_("message"), max_length=255)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default=ACTION_LIKE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]



"""
Signal
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Like)
def notify_like_create(sender, instance, created, **kwargs):
    if created and instance.user != instance.project.author:
        # Buat notifikasi
        notification = Notification.objects.create(
            user=instance.project.author,
            sender=instance.user, # Simpan siapa yang melakukan like
            message=f"@{instance.user.username} menyukai proyek Anda: {instance.project.title}",
            project=instance.project,
            action_type='like',
        )
        
        # Kirim ke WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notify_{instance.project.author.id}",
            {
                "type": "send_notification",
                "notification_id": str(notification.id), # Kirim ID agar bisa dihapus nanti
                "message": notification.message,
                "action": "create"
            }
        )

@receiver(post_delete, sender=Like)
def notify_like_delete(sender, instance, **kwargs):
    # Cari dan hapus notifikasi yang sesuai
    notifications = Notification.objects.filter(
        user=instance.project.author,
        sender=instance.user,
        project=instance.project,
        action_type='like',
    )
    
    if notifications.exists():
        for note in notifications:
            # Beri tahu frontend untuk menghapus notifikasi ini
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notify_{instance.project.author.id}",
                {
                    "type": "send_notification",
                    "notification_id": str(note.id),
                    "action": "delete" # Instruksi untuk hapus di UI
                }
            )
        notifications.delete()


@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created and instance.user != instance.project.author:
        notification = Notification.objects.create(
            user=instance.project.author,
            message=f"@{instance.user.username} mengomentari proyek Anda: {instance.project.title}",
            project=instance.project,
            action_type="comment"
        )
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notify_{instance.project.author.id}",
            {
                "type": "send_notification",
                "message": notification.message,
                "notification_id": str(notification.id),
                "action": "create"
            }
        )


@receiver(post_delete, sender=Comment)
def notify_comment_delete(sender, instance, **kwargs):
    # Cari dan hapus notifikasi yang sesuai
    notifications = Notification.objects.filter(
        user=instance.project.author,
        sender=instance.user,
        project=instance.project,
        action_type='comment',
    )
    
    if notifications.exists():
        for note in notifications:
            # Beri tahu frontend untuk menghapus notifikasi ini
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notify_{instance.project.author.id}",
                {
                    "type": "send_notification",
                    "notification_id": str(note.id),
                    "action": "delete" # Instruksi untuk hapus di UI
                }
            )
        notifications.delete()