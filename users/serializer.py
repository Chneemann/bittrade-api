import re
from rest_framework import serializers
from django.core.validators import MinLengthValidator
from rest_framework.validators import UniqueValidator
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

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email already exists")]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Username already exists")]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'verified', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'verified']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'password': {'required': False},
            'verified': {'required': False}
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
        email = self.validated_data.get("email")
        return bool(email and email != self.instance.email)

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
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)
        verified = validated_data.pop('verified', None)
        
        if email and email != instance.email:
            instance.unconfirmed_email = email
            self.send_email_verification(instance)

        if password:
            instance.password = make_password(password)

        if verified is True and not instance.verified:
            instance.verified = True

        instance = super().update(instance, validated_data)
        instance.save()
        return instance