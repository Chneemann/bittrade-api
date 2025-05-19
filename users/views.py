from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import LoginSerializer
from django.contrib.auth import authenticate
from rest_framework import status

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user:
                if not user.is_active:
                    return Response({'error': 'Account is inactive, please check your mails'}, status=status.HTTP_403_FORBIDDEN)
            return Response({'error': 'Unable to login with provided credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
          
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
