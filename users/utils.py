from django.utils import timezone
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from .models import ExpiringToken
from config.settings import TOKEN_EXPIRATION_TIME
from django.conf import settings

def set_auth_cookie(response, token_key, max_age):
    response.set_cookie(
        key='auth_token',
        value=token_key,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=int(max_age.total_seconds()),
        path='/',
    )
    return response

def create_token_response(user):
    now = timezone.now()

    with transaction.atomic():
        token, created = ExpiringToken.objects.select_for_update().get_or_create(user=user)

        if token.is_expired():
            token.delete()
            token = ExpiringToken.objects.create(user=user)

        token.expires_at = now + TOKEN_EXPIRATION_TIME
        token.save()

    user.last_login = now
    user.save(update_fields=['last_login'])

    res = Response({'detail': 'Login successful'}, status=status.HTTP_200_OK)
    return set_auth_cookie(res, token.key, TOKEN_EXPIRATION_TIME)