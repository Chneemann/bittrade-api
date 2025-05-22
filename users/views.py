from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import LoginSerializer
from .utils import create_token_response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

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

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)

            if user:
                if not user.is_active:
                    return Response({'error': 'Account is inactive, please check your mails'}, status=403)
                return create_token_response(user)

            return Response({'error': 'Unable to login with provided credentials.'}, status=401)

        return Response(serializer.errors, status=400)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response(status=200)
        response.delete_cookie('auth_token', path='/', domain=None)
        return response