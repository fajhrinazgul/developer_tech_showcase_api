from rest_framework import serializers
from .models import Notification



class NotificationSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    
    class Meta:
        model = Notification
        fields = ["id", "message", "is_read", "created_at", 
                  "project", "project_title",]
        read_only_fields = ["created_at", "project_title"]
        