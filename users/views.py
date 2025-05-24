from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import LoginSerializer
from .utils import create_token_response, ratelimit_response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.decorators import method_decorator


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit_response(rate='10/m', method='GET'))
    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            "id": str(user.id),
            "email": user.email,
        })

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @method_decorator(ratelimit_response(rate='5/m', method='POST'))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'message': 'Invalid input data.'
            }, status=400)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({
                'error': 'authentication_failed',
                'message': 'Email or password is incorrect.'
            }, status=401)

        if not user.is_active:
            return Response({
                'error': 'account_inactive',
                'message': 'Account inactive. Please check your email.'
            }, status=403)

        return create_token_response(user)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = Response(status=200)
        response.delete_cookie('auth_token', path='/', domain=None)
        return response