from allauth.account.models import get_emailconfirmation_model
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from .serializers import  CustomRegisterSerializer


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer
class CustomVerifyEmailView(VerifyEmailView):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'detail': 'Invalid verification key.'
            }, status=status.HTTP_400_BAD_REQUEST)

        self.kwargs['key'] = serializer.validated_data['key']
        key = self.kwargs["key"]
        model = get_emailconfirmation_model()
        confirmation = model.from_key(key)
        if not confirmation:
            return Response({
                'detail': 'Invalid Key or Your email has already been confirmed .'
            }, status=status.HTTP_400_BAD_REQUEST)
        email_address = confirmation.email_address

        try:
            confirmation.confirm(self.request)
            return Response({
                'detail': f'{email_address.email}  has been successfully confirmed.'
            }, status=status.HTTP_200_OK)

        except APIException as e:
            return Response({
                'detail': f'Error confirming email: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'detail': f'An unexpected error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






