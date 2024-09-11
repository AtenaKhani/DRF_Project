import pytest

from datetime import date

from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


pytestmark=pytest.mark.django_db

class TestUserProfile:
    endpoint=reverse('profile')

    def test__request_with_valid_jwt_token_should_be_accepted_and_return_200(self, user_instance,api_client):
        url = self.endpoint
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test__request_with_invalid_jwt_token_should_be_rejected_and_return_401(self, user_instance,api_client):
        url = self.endpoint
        access_token = 'invalid_token'
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == "Given token not valid for any token type"

    def test__unauthenticated_request_should_be_rejected_and_return_401(self, ad_instance,api_client):
        url = self.endpoint
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    def test__user_profile_displays_correct_user_information(self,user_instance,api_client):
        url = self.endpoint
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['pk']== user_instance.id
        assert response.data['email'] == user_instance.email
        assert float(response.data['wallet_balance']) == float(user_instance.wallet_balance)

    def test__put_request_to_updeta_user_information_with_valid_data_accepted_and_return_200(self, new_user,user_instance,api_client):
        data={'first_name':'atena','last_name':'khani','birth_date':date(2003,1,1),'phone_number':'+989196339457'}
        url=self.endpoint
        api_client.force_authenticate(user=user_instance)
        response = api_client.put(url, data=data, format='json')
        user_instance.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == data['first_name']
        assert user_instance.first_name == data['first_name']
        assert response.data['phone_number'] == data['phone_number']
        assert user_instance.phone_number ==  data['phone_number']

    def test__put_request_to_updeta_user_information_with_invalid_date_and_last_name_rejected_and_return_400(self, new_user,user_instance,api_client):
        data={'first_name':'atena','last_name':'a123','birth_date':date(2025,1,1),'phone_number':'+989196339457'}
        url=self.endpoint
        api_client.force_authenticate(user=user_instance)
        response = api_client.put(url, data=data, format='json')
        user_instance.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['last_name'][0] == "Last name must contain only alphabetic characters."
        assert response.data['birth_date'][0] == "Birth date cannot be in the future."

class TestCustomLogin:
   endpoint=reverse('login')
   def test__post_request_to_login_by_verified_user_with_valid_data_accepted_and_return_200(self,verified_user,api_client):
       url=self.endpoint
       verified_user.set_password('yourpassword')
       verified_user.save()
       data={'email':verified_user.email,'password':'yourpassword'}
       response = api_client.post(url, data=data, format='json')
       assert response.status_code == status.HTTP_200_OK
       assert response.data['detail'] == "Successfully logged in"


   def test__post_request_to_login_by_verified_user_with_invalid_password_rejectedd_and_return_400(self,verified_user,api_client):
       url=self.endpoint
       verified_user.set_password('yourpassword')
       verified_user.save()
       data={'email':verified_user.email,'password':'invalid_password'}
       response = api_client.post(url, data=data, format='json')
       assert response.status_code == status.HTTP_400_BAD_REQUEST
       assert response.data['non_field_errors'][0] == 'Incorrect password.'

   def test__post_request_to_login_by_unverified_user_with_valid_data_rejectedd_and_return_400(self,verified_user,api_client):
       url = self.endpoint
       EmailAddress.objects.filter(user=verified_user).update(verified=False)
       verified_user.set_password('yourpassword')
       verified_user.save()
       data = {'email': verified_user.email, 'password': 'yourpassword'}
       response = api_client.post(url, data=data, format='json')
       assert response.status_code == status.HTTP_400_BAD_REQUEST
       assert response.data['non_field_errors'][0] == 'E-mail is not verified.'

   def test_post_request_to_login_with_inactive_user_rejected_and_return_200(self,verified_user,api_client):
       url = self.endpoint
       verified_user.is_active = False
       verified_user.save()
       verified_user.set_password('yourpassword')
       verified_user.save()
       data = {'email': verified_user.email, 'password': 'yourpassword'}
       response = api_client.post(url, data=data, format='json')
       assert response.status_code == status.HTTP_400_BAD_REQUEST
       assert response.data['non_field_errors'][0] == 'User account is disabled.'

   def test__post_request_by_user_not_registered_yet_rejected_and_return_400(self,api_client):
       url = self.endpoint
       data = {'email': 'nonexistent@example.com', 'password': 'some_password'}
       response = api_client.post(url, data=data, format='json')
       assert response.status_code == status.HTTP_400_BAD_REQUEST
       assert response.data['non_field_errors'][0] == 'No user found with this email address.'

class TestCustomRegister:
   endpoint=reverse('registration')
   def test__post_request_to_register_with_valid_data_accepted_and_return_201(self,api_client):
       url=self.endpoint
       data = {'email': 'test@gmail.com', 'password1': 'Tt*40015091006', 'password2': 'Tt*40015091006'}
       response = api_client.post(url, data=data, format='json')
       assert response.status_code == status.HTTP_201_CREATED
       assert response.data['detail'] ==  "Verification e-mail sent."


   def test__post_request_to_register_with_duplicated_email_rejected_and_return_400(self,api_client,verified_user):
       url=self.endpoint
       data = {'email': verified_user.email, 'password1': 'Tt*40015091006', 'password2': 'Tt*40015091006'}
       response = api_client.post(url, data=data, format='json')
       assert response.status_code == status.HTTP_400_BAD_REQUEST
       assert response.data['email'][0] ==   "A user is already registered with this e-mail address."


   def test__post_request_to_register_fails_when_passwords_do_not_match_and_return_400(self,api_client):
        url = self.endpoint
        data = {'email': 'test2@gmail.com', 'password1': 'Tt*40015091006', 'password2': 'Ss*40015091006'}
        response = api_client.post(url, data=data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"][0] == "The two password fields didn't match."

   def test__post_request_to_register_fails_when_email_invalid_and_return_400(self, api_client):
       url = self.endpoint
       data = {'email': 'aaaaarfgtyh', 'password1': 'Tt*40015091006', 'password2': 'Ss*40015091006'}
       response = api_client.post(url, data=data, format='json')
       assert response.status_code == status.HTTP_400_BAD_REQUEST
       assert response.data["email"][0] ==  "Enter a valid email address."


   def test__post_request_to_register_fails_when_email_is_empty_and_return_400(self,api_client):
        url = self.endpoint
        data = {'email': '', 'password1': 'Tt*40015091006', 'password2': 'Ss*40015091006'}
        response = api_client.post(url, data=data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["email"][0] == "This field may not be blank."

   def test__post_request_to_register_fails_when_password_is_empty_and_return_400(self,api_client):
        url = self.endpoint
        data = {'email': 'test2@gmail.com', 'password1': '', 'password2': ''}
        response = api_client.post(url, data=data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["password1"][0] == "This field may not be blank."
        assert response.data["password2"][0] == "This field may not be blank."

   def test__post_request_to_register_fails_when_password_is_short_return_400(self,api_client):
        url = self.endpoint
        data = {'email': 'test2@gmail.com', 'password1': '123', 'password2': '123'}
        response = api_client.post(url, data=data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["password1"][0] == "This password is too short. It must contain at least 8 characters."

   def test__post_request_to_register_fails_when_password_is_too_common_return_400(self,api_client):
        url = self.endpoint
        data = {'email': 'test2@gmail.com', 'password1': 'Aa123456', 'password2': 'Aa123456'}
        response = api_client.post(url, data=data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["password1"][0] == "This password is too common."















