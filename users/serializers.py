import re
from datetime import date
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework import exceptions,serializers
from django.urls import exceptions as url_exceptions
from allauth.account import app_settings as allauth_account_settings
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import CustomUser


UserModel = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')
class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
            if not user:
                UserModel = get_user_model()
                try:
                    UserModel.objects.get(email=email)
                    raise exceptions.ValidationError('Incorrect password.')
                except UserModel.DoesNotExist:
                    raise exceptions.ValidationError('No user found with this email address.')
        else:
            msg = 'Must include "email" and "password".'
            raise exceptions.ValidationError(msg)

        return user

    def get_auth_user_using_allauth(self, email, password):
        if allauth_account_settings.AUTHENTICATION_METHOD == allauth_account_settings.AuthenticationMethod.EMAIL:
            return self._validate_email(email, password)

        msg = 'This authentication method is not supported. Please use email for login.'
        raise exceptions.ValidationError(msg)

    def get_auth_user(self, email, password):
        if 'allauth' in settings.INSTALLED_APPS:
            try:
                return self.get_auth_user_using_allauth(email, password)
            except url_exceptions.NoReverseMatch:
                msg = 'Unable to log in with provided credentials.'
                raise exceptions.ValidationError(msg)
        else:
            return self._validate_email(email, password)
    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = 'User account is disabled.'
            raise exceptions.ValidationError(msg)

    @staticmethod
    def validate_email_verification_status(user, email=None):

        if (
            allauth_account_settings.EMAIL_VERIFICATION == allauth_account_settings.EmailVerificationMethod.MANDATORY and not user.emailaddress_set.filter(email=user.email, verified=True).exists()
        ):
            raise serializers.ValidationError('E-mail is not verified.')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = self._validate_email(email, password)
        self.validate_auth_user_status(user)
        if 'dj_rest_auth.registration' in settings.INSTALLED_APPS:
            self.validate_email_verification_status(user, email=email)

        attrs['user'] = user
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
        'pk', 'email', 'first_name', 'last_name', 'birth_date', 'phone_number', 'wallet_balance', 'date_joined')
        read_only_fields = ('email', 'date_joined', 'wallet_balance')

    def validate_birth_date(self, value):
        if value is None:
            raise serializers.ValidationError("Birth date is required.")
        today = date.today()
        if value > today:
            raise serializers.ValidationError("Birth date cannot be in the future.")
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 7:
            raise serializers.ValidationError("You must be at least 7 years old.")
        if age > 100:
            raise serializers.ValidationError("Age must be less than 100 years.")

        return value

    def validate_name_field(self, value, field_name):
        if not value:
            raise serializers.ValidationError(f"{field_name} cannot be empty.")
        if len(value) < 3:
            raise serializers.ValidationError(f"{field_name} must be at least 3 characters long.")
        if not re.match(r'^[A-Za-zآ-ی]+$', value):
            raise serializers.ValidationError(f"{field_name} must contain only alphabetic characters.")
        return value

    def validate_first_name(self, value):
        return self.validate_name_field(value, "First name")

    def validate_last_name(self, value):
        return self.validate_name_field(value, "Last name")




