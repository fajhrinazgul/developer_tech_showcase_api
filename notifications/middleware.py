from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        access_token = AccessToken(token_key)
        username = access_token['username']
        return User.objects.get(username=username)
    except Exception:
        # Jika token expired atau invalid, kembalikan None
        return None

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # 1. Ambil query string
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        
        # 2. Ambil token (parse_qs mengembalikan list, ambil index ke-0)
        token_list = query_params.get("access_token")
        token = token_list[0] if token_list else None
        
        # 3. Validasi User
        user = AnonymousUser()
        if token:
            found_user = await get_user_from_token(token)
            if found_user:
                user = found_user
        
        # 4. SET scope['user'] (PENTING: Jangan sampai KeyError)
        scope["user"] = user
        return await self.inner(scope, receive, send)