import jwt
import time
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User

_user_cache: dict = {}
_USER_TTL = 60  # seconds — re-validate user from DB at most once per minute


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        if not header.startswith('Bearer '):
            return None
        token = header[7:]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        if payload.get('type') != 'access':
            raise AuthenticationFailed('Invalid token type.')

        user_id = payload['sub']
        now = time.monotonic()
        cached = _user_cache.get(user_id)
        if cached and now - cached['ts'] < _USER_TTL:
            return (cached['user'], token)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')

        if not user.is_active:
            raise AuthenticationFailed('Account disabled.')

        _user_cache[user_id] = {'user': user, 'ts': now}
        return (user, token)


def invalidate_user(user_id: str) -> None:
    _user_cache.pop(str(user_id), None)
