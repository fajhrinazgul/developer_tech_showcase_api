from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import asyncio
from django.db import close_old_connections

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        # Validate and decode the access token using SimpleJWT
        validated_token = AccessToken(token_key)
        user_id = validated_token['username']
        return User.objects.get(username=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Hapus close_old_connections di awal untuk mempercepat HTTP router
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        token = query_params.get("access_token", [None])[0]
        
        scope["user"] = AnonymousUser()
        
        if token:
            try:
                # Jangan gunakan timeout terlalu singkat jika DB sedang sibuk
                user = await get_user_from_token(token)
                if user:
                    scope["user"] = user
            except Exception as e:
                print(f"Auth Error: {e}")
        
        # Panggil inner app
        return await self.inner(scope, receive, send)