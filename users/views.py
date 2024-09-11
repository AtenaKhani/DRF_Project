import logging

from allauth.account.models import get_emailconfirmation_model
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView
from dj_rest_auth.views import LoginView, PasswordChangeView
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import CustomRegisterSerializer, CustomLoginSerializer, UserProfileSerializer
from .throttle import  LoginRateThrottle

logger=logging.getLogger('users')

class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


class CustomVerifyEmailView(VerifyEmailView):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.warning("Email verification failed: Invalid verification key provided.")
            return Response({
                'detail': 'Invalid verification key.'
            }, status=status.HTTP_400_BAD_REQUEST)

        self.kwargs['key'] = serializer.validated_data['key']
        key = self.kwargs["key"]
        model = get_emailconfirmation_model()
        confirmation = model.from_key(key)
        if not confirmation:
            logger.warning("Email verification failed: Invalid key or email already confirmed.")
            return Response({
                'detail': 'Invalid Key or Your email has already been confirmed .'
            }, status=status.HTTP_400_BAD_REQUEST)
        email_address = confirmation.email_address

        try:
            confirmation.confirm(self.request)
            logger.info(f"Email confirmed successfully for address: {email_address.email}")
            return Response({
                'detail': f'{email_address.email}  has been successfully confirmed.'
            }, status=status.HTTP_200_OK)

        except APIException as e:
            logger.error(f"Error confirming email: {str(e)}")
            return Response({
                'detail': f'Error confirming email: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return Response({
                'detail': f'An unexpected error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomLoginView(LoginView):
    throttle_classes = [LoginRateThrottle]
    serializer_class = CustomLoginSerializer
    def get_response(self):
        logger.info("Login successful, preparing response.")
        return Response({
            'detail': f'Successfully logged in'
        }, status=status.HTTP_200_OK)

class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return get_user_model().objects.none()


class CustomPasswordChangeView(PasswordChangeView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

