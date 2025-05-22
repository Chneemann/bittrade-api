from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import LoginSerializer
from django.contrib.auth import authenticate
from rest_framework import status
from django.utils import timezone
from .models import ExpiringToken
from config.settings import TOKEN_EXPIRATION_TIME
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": str(user.id),
            "email": user.email,
        })
    
class LoginView(APIView):
    permission_classes = [AllowAny] 
    serializer_class = LoginSerializer

    def _create_token_response(self, user):
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

        return Response({'token': token.key}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)

            if user:
                if not user.is_active:
                    return Response({'error': 'Account is inactive, please check your mails'}, status=403)
                return self._create_token_response(user)

            return Response({'error': 'Unable to login with provided credentials.'}, status=401)

        return Response(serializer.errors, status=400)