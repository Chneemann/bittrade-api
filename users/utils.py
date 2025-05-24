from django.utils import timezone
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from .models import ExpiringToken
from config.settings import TOKEN_EXPIRATION_TIME
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from functools import wraps

def set_auth_cookie(response, token_key, max_age):
    """
    Sets the auth_token cookie on the response with secure flags.
    """
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
    """
    Creates or renews an ExpiringToken for the user, 
    updates the expiration, and sets the auth cookie in the response.
    """
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

def ratelimit_response(key='ip', rate='5/m', method='POST'):
    """
    Custom decorator wrapping django-ratelimit with a 
    friendly JSON response on rate limit hit.
    """
    def decorator(view_func):
        @ratelimit(key=key, rate=rate, method=method, block=False)
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if getattr(request, 'limited', False):
                return Response({
                    'error': 'rate_limit_exceeded',
                    'message': 'Too many requests. Please try again later.'
                }, status=429)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator