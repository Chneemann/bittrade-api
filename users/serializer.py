from rest_framework import serializers
from django.core.validators import MinLengthValidator

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(validators=[MinLengthValidator(limit_value=8)])

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email:
            raise serializers.ValidationError("Email is required.")
        
        if not password:
            raise serializers.ValidationError("Password is required.")
        
        return data
