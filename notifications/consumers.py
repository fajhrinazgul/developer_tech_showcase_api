import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Setelah dipastikan ada, baru cek is_anonymous
        # print(self.scope["user"].is_anonymous)
        if self.scope["user"].is_anonymous:
            await self.close(code=4003)
        else:
            self.group_name = f"notify_{self.scope['user'].id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
    
    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            group_name = self.group_name
            print("websocket disconnected,", code)
            await self.channel_layer.group_discard(group_name, self.channel_name)
            raise StopConsumer()
        raise StopConsumer()
        
    async def send_notification(self, event):
        # Mengirim payload lengkap untuk diproses frontend
        await self.send(text_data=json.dumps({
            "action": event["action"], # "create" atau "delete"
            "notification_id": event.get("notification_id"),
            "message": event.get("message"),
            "to_user": event.get("to_user"),
        }))