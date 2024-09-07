from django.contrib.auth import get_user_model
from rest_framework import  serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import CustomUser


UserModel = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

