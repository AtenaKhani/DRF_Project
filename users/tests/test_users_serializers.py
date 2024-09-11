from datetime import date

import pytest
from allauth.account.models import EmailAddress

from rest_framework.exceptions import ValidationError

from users.serializers import UserProfileSerializer,CustomLoginSerializer


pytestmark=pytest.mark.django_db

class TestUserProfile:
    def test__validate_birth_sate_with_valid_date(self,new_user):
        serializer = UserProfileSerializer(data=new_user)
        assert serializer.is_valid()
        assert serializer.validated_data['birth_date'] == new_user['birth_date']


    def test__validate_birth_date_with_none_date(self,new_user):
        new_user['birth_date'] = None
        serializer = UserProfileSerializer(data=new_user)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
        assert 'birth_date' in serializer.errors
        assert serializer.errors['birth_date'][0] == "Birth date is required."

    def test__validate_birth_date_with_future_date(self,new_user):
        new_user['birth_date'] = date(2024,11,4)
        serializer = UserProfileSerializer(data=new_user)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
        assert 'birth_date' in serializer.errors
        assert serializer.errors['birth_date'][0] == "Birth date cannot be in the future."


    def test__validate_birth_date_with_too_old_age(self,new_user):
            new_user['birth_date'] = date(1900,1,1)
            serializer = UserProfileSerializer(data=new_user)
            with pytest.raises(ValidationError):
                serializer.is_valid(raise_exception=True)
            assert 'birth_date' in serializer.errors
            assert serializer.errors['birth_date'][0] == "Age must be less than 100 years."


    def test__validate_birth_date_with_too_yong_age(self,new_user):
            new_user['birth_date'] = date(2024,1,1)
            serializer = UserProfileSerializer(data=new_user)
            with pytest.raises(ValidationError):
                serializer.is_valid(raise_exception=True)
            assert 'birth_date' in serializer.errors
            assert serializer.errors['birth_date'][0] == "You must be at least 7 years old."

    def test__validate_name_field_with_valid_first_name(self, new_user):
        new_user['first_name'] = "atena"
        serializer = UserProfileSerializer(data=new_user)
        assert  serializer.is_valid()
        assert serializer.validated_data['first_name'] == new_user['first_name']

    def test__validate_name_field_with_valid_last_name(self, new_user):
        new_user['last_name'] = "khani"
        serializer = UserProfileSerializer(data=new_user)
        assert serializer.is_valid()
        assert serializer.validated_data['last_name'] == new_user['last_name']


    def test__validate_name_field_with_short_name(self,new_user):
        new_user['first_name'] = "ak"
        serializer = UserProfileSerializer(data=new_user)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
        assert 'first_name' in serializer.errors
        assert serializer.errors['first_name'][0] == "First name must be at least 3 characters long."

    def test__validate_name_field_with_invalid_characters(self, new_user):
        new_user['first_name'] = "ak123"
        serializer = UserProfileSerializer(data=new_user)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
        assert 'first_name' in serializer.errors
        assert serializer.errors['first_name'][0] == "First name must contain only alphabetic characters."

    class TestUserProfile:

        def test__validate_email_and_password__by_verified_user_and_valid_data(self,verified_user):
                data = {
                    'email': 'test@example.com',
                    'password': 'valid_password'
                }
                serializer = CustomLoginSerializer(data=data, context={'request': None})
                assert serializer.is_valid()
                assert serializer.validated_data['user'] == verified_user

        def test__validate_email_and_password__by_verified_user_with_incorrect_password(self,verified_user):
            data = {
                'email': 'test@example.com',
                'password': 'invalid_password'
            }
            serializer = CustomLoginSerializer(data=data, context={'request': None})
            is_valid = serializer.is_valid()
            assert not is_valid
            assert serializer.errors['non_field_errors'][0] == 'Incorrect password.'

        def test__validate_email_and_password__by_unverified_user(self,verified_user):
            EmailAddress.objects.filter(user=verified_user).update(verified=False)
            data = {
                'email': 'test@example.com',
                'password': 'valid_password'
            }
            serializer = CustomLoginSerializer(data=data, context={'request': None})
            is_valid = serializer.is_valid()
            assert not is_valid
            assert serializer.errors['non_field_errors'][0] == 'E-mail is not verified.'

        def test__validate_email_with_user_not_exist(self):
            data = {'email': 'nonexistent@example.com', 'password': 'some_password'}
            serializer = CustomLoginSerializer(data=data,context={'request': None})

            with pytest.raises(ValidationError) :
                serializer.is_valid(raise_exception=True)
            assert serializer.errors['non_field_errors'][0] ==  'No user found with this email address.'

        def test__validate_email_with_empty_field(self):
            data = {'email': '', 'password': ''}
            serializer = CustomLoginSerializer(data=data,context={'request': None})
            with pytest.raises(ValidationError) :
                serializer.is_valid(raise_exception=True)
            assert serializer.errors['email'][0] ==   "This field may not be blank."
            assert serializer.errors['password'][0] == "This field may not be blank."

        def test_validate_user_inactive(self,verified_user):
            verified_user.is_active = False
            verified_user.save()
            data = {
                'email': 'test@example.com',
                'password': 'valid_password'
            }
            serializer = CustomLoginSerializer(data=data,context={'request': None})
            with pytest.raises(ValidationError) :
                serializer.is_valid(raise_exception=True)
            assert serializer.errors['non_field_errors'][0] == 'User account is disabled.'









