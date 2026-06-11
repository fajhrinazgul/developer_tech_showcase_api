import threading
from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from projects.models import Project, Like, Comment
import uuid
from users.models import Follow
User = get_user_model()


class Notification(models.Model):
    ACTION_LIKE = 'like'
    ACTION_COMMENT = 'comment'
    ACTION_FOLLOW = "follow"
    ACTION_CHOICES = [(ACTION_LIKE, 'Like'), (ACTION_COMMENT, 'Comment'), (ACTION_FOLLOW, "Follow")]
    
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications", null=True)
    message = models.CharField(_("message"), max_length=255, blank=True, null=True)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default=ACTION_LIKE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]




# =====================================================================
# REUSABLE WORKER (Fungsi khusus untuk mengirim WS di thread terpisah)
# =====================================================================
def run_ws_broadcast(group_name, payload):
    """
    Fungsi ini berjalan di thread mandiri, sehingga aman dari deadlock
    dan tidak akan pernah membuat request HTTP Django menggantung.
    """
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, payload)
    except Exception as e:
        print(f"--- [WS Background Thread Error] : {e} ---")

# ==========================================
# SIGNALS FOR LIKE SYSTEM
# ==========================================

@receiver(post_save, sender=Like)
def notify_like_create(sender, instance, created, **kwargs):
    if created and instance.user != instance.project.author:
        # print(f"DEBUG: Signal LIKE dipicu! Created={created}")
        # PENGAMAN: Cek apakah notifikasi untuk aksi ini sudah ada (mencegah duplikasi)
        notification, was_created = Notification.objects.get_or_create(
            user=instance.project.author,
            sender=instance.user,
            project=instance.project,
            action_type='like',
            defaults={'message': f"@{instance.user.username} likes your project: {instance.project.title}"}
        )

        # Hanya kirim WebSocket jika notifikasi BARU saja dibuat
        if was_created:
            def send_ws():
                threading.Thread(
                    target=run_ws_broadcast,
                    args=(
                        f"notify_{instance.project.author.id}",
                        {
                            "type": "send_notification",
                            "notification_id": str(notification.id),
                            "message": notification.message,
                            "action": "create",
                            "to_user": str(instance.project.author.id),
                        }
                    ),
                    daemon=True
                ).start()
            transaction.on_commit(send_ws)


@receiver(post_delete, sender=Like)
def notify_like_delete(sender, instance, **kwargs):
    notifications = list(Notification.objects.filter(
        user=instance.project.author,
        sender=instance.user,
        project=instance.project,
        action_type='like',
    ))
    
    if notifications:
        def delete_ws():
            for note in notifications:
                threading.Thread(
                    target=run_ws_broadcast,
                    args=(
                        f"notify_{instance.project.author.id}",
                        {
                            "type": "send_notification",
                            "notification_id": str(note.id),
                            "action": "delete",
                            "message": None,
                            "to_user": str(instance.project.author.id),
                        }
                    ),
                    daemon=True
                ).start()
            Notification.objects.filter(id__in=[n.id for n in notifications]).delete()
            
        transaction.on_commit(delete_ws)


# ==========================================
# SIGNALS FOR COMMENT SYSTEM
# ==========================================

@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created and instance.user != instance.project.author:
        notification = Notification.objects.create(
            user=instance.project.author,
            sender=instance.user,
            message=f"@{instance.user.username} commented on your project: {instance.project.title}",
            project=instance.project,
            action_type="comment"
        )
        
        def send_ws():
            threading.Thread(
                target=run_ws_broadcast,
                args=(
                    f"notify_{instance.project.author.id}",
                    {
                        "type": "send_notification",
                        "message": notification.message,
                        "notification_id": str(notification.id),
                        "action": "create",
                        "to_user": str(instance.project.author.id),
                    }
                ),
                daemon=True
            ).start()
            
        transaction.on_commit(send_ws)


@receiver(post_delete, sender=Comment)
def notify_comment_delete(sender, instance, **kwargs):
    notifications = list(Notification.objects.filter(
        user=instance.project.author,
        sender=instance.user,
        project=instance.project,
        action_type='comment',
    ))
    
    if notifications:
        def delete_ws():
            for note in notifications:
                threading.Thread(
                    target=run_ws_broadcast,
                    args=(
                        f"notify_{instance.project.author.id}",
                        {
                            "type": "send_notification",
                            "notification_id": str(note.id),
                            "action": "delete",
                            "message": None,
                            "to_user": str(instance.project.author.id),
                        }
                    ),
                    daemon=True
                ).start()
            Notification.objects.filter(id__in=[n.id for n in notifications]).delete()
            
        transaction.on_commit(delete_ws)


# ==========================================
# SIGNALS FOR FOLLOW SYSTEM
# ==========================================

@receiver(post_save, sender=Follow)
def notify_create_follow(sender, instance, created, **kwargs):
    # Memastikan dia membuat follow baru dan tidak memfollow diri sendiri
    if created and instance.follower != instance.following:
        notification, was_created = Notification.objects.get_or_create(
            user=instance.following,
            sender=instance.follower,
            project=None,
            action_type=Notification.ACTION_FOLLOW,
            defaults={"message": f"@{instance.follower.username} started following you."}
        )
        
        if was_created:
            def send_ws():
                threading.Thread(
                    target=run_ws_broadcast,
                    args=(
                        f"notify_{instance.following.id}",
                        {
                            "type": "send_notification",
                            "notification_id": str(notification.id),
                            "message": notification.message,
                            "action": "create",
                            "to_user": str(instance.following.id),
                        }
                    ),
                    daemon=True,
                ).start()
            transaction.on_commit(send_ws)


@receiver(post_delete, sender=Follow)
def notify_follow_delete(sender, instance, **kwargs):
    notifications = list(Notification.objects.filter(
        user=instance.following,
        sender=instance.follower,
        action_type=Notification.ACTION_FOLLOW,
    ))
    
    if notifications:
        def delete_ws():
            for note in notifications:
                threading.Thread(
                    target=run_ws_broadcast,
                    args=(
                        f"notify_{instance.following.id}",
                        {
                            "type": "send_notification",
                            "notification_id": str(note.id),
                            "action": "delete",
                            "message": None,
                            "to_user": str(instance.following.id)
                        }
                    ),
                    daemon=True
                ).start()
            Notification.objects.filter(id__in=[n.id for n in notifications]).delete()
        transaction.on_commit(delete_ws)