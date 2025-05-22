from rest_framework.authentication import TokenAuthentication
from .models import ExpiringToken

class CookieTokenAuthentication(TokenAuthentication):
    model = ExpiringToken 

    def authenticate(self, request):
        token = request.COOKIES.get('auth_token')
        if not token:
            return None
        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            return None

        if token.is_expired() or not token.user.is_active:
            return None

        return (token.user, token)