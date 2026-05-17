import jwt
import logging
import datetime
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .tokens import make_access_token, make_refresh_token, decode_refresh_token
from .authentication import invalidate_user
from core.responses import ok, err

logger = logging.getLogger(__name__)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')
    if not email or not password:
        return err('Email and password are required.', 400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return err('Invalid credentials.', 401)
    except Exception as e:
        logger.error('DB error during login for %s: %s', email, e, exc_info=True)
        return err('Internal server error.', 500)

    if not user.is_active:
        return err('Account disabled.', 403)

    if not check_password(password, user.password_hash):
        return err('Invalid credentials.', 401)

    try:
        access = make_access_token(str(user.id))
        refresh = make_refresh_token(str(user.id))
    except Exception as e:
        logger.error('Token generation failed for %s: %s', email, e, exc_info=True)
        return err('Internal server error.', 500)

    return ok({
        'access': access,
        'refresh': refresh,
        'user': {'id': str(user.id), 'email': user.email, 'name': user.name},
    })


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def refresh(request):
    token = request.data.get('refresh', '')
    if not token:
        return err('Refresh token required.', 400)
    try:
        user_id = decode_refresh_token(token)
    except jwt.ExpiredSignatureError:
        return err('Refresh token expired.', 401)
    except jwt.InvalidTokenError:
        return err('Invalid refresh token.', 401)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return err('User not found.', 401)

    if not user.is_active:
        return err('Account disabled.', 403)

    return ok({'access': make_access_token(str(user.id))})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return ok({'id': str(user.id), 'email': user.email, 'name': user.name})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_me(request):
    user = request.user
    if 'name' in request.data:
        user.name = request.data['name'].strip()
    if 'password' in request.data:
        pw = request.data['password']
        if len(pw) < 6:
            return err('Password must be at least 6 characters.', 400)
        user.password_hash = make_password(pw)
    user.save()
    invalidate_user(str(user.id))
    return ok({'id': str(user.id), 'email': user.email, 'name': user.name})
