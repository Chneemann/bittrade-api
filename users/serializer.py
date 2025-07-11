import re
from rest_framework import serializers
from django.core.validators import MinLengthValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.hashers import make_password

User = get_user_model()

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

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
        }

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use")
        return value
    
    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken")

        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores")

        if len(value) < 8:
            raise serializers.ValidationError("Username must be at least 8 characters long")

        return value
        
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value
    
    def is_email_changed(self):
        new_email = self.validated_data.get("email")
        return bool(new_email and new_email != self.instance.email)

    def send_email_verification(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verify_url = f"http://localhost:4200/auth/verify-email/?uid={uid}&token={token}"

        send_mail(
            subject="Confirm your new email",
            message=f"Click the link to confirm your new email address: {verify_url}",
            from_email="noreply@your-domain.com",
            recipient_list=[user.unconfirmed_email],
        )

    def update(self, instance, validated_data):
        new_email = validated_data.get('email')
        new_password = validated_data.pop('password', None)

        if new_email and new_email != instance.email:
            instance.unconfirmed_email = new_email
            self.send_email_verification(instance)
            validated_data.pop('email', None) 

        if new_password:
            instance.password = make_password(new_password)

        instance = super().update(instance, validated_data)
        instance.save()
        return instance