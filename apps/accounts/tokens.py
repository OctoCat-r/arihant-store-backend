import jwt
import datetime
from django.conf import settings


def _make_token(user_id: str, token_type: str, ttl: datetime.timedelta) -> str:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    payload = {
        'sub': user_id,
        'type': token_type,
        'iat': now,
        'exp': now + ttl,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def make_access_token(user_id: str) -> str:
    ttl = datetime.timedelta(hours=settings.JWT_ACCESS_TTL_HOURS)
    return _make_token(user_id, 'access', ttl)


def make_refresh_token(user_id: str) -> str:
    ttl = datetime.timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
    return _make_token(user_id, 'refresh', ttl)


def decode_refresh_token(token: str) -> str:
    """Returns user_id or raises jwt.InvalidTokenError."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    if payload.get('type') != 'refresh':
        raise jwt.InvalidTokenError('Not a refresh token.')
    return payload['sub']
