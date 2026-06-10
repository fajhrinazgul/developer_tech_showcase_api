import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Setelah dipastikan ada, baru cek is_anonymous
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.group_name = f"notify_{self.scope['user'].id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        
    async def send_notification(self, event):
        # Mengirim payload lengkap untuk diproses frontend
        await self.send(text_data=json.dumps({
            "action": event["action"], # "create" atau "delete"
            "notification_id": event.get("notification_id"),
            "message": event.get("message")
        }))