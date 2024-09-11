import pytest
from django.contrib.auth import get_user_model

pytestmark=pytest.mark.django_db

class TestAdModel:
    @pytest.mark.django_db
    def test__test_user_access(self,user_instance):
        print(user_instance)


User=get_user_model()
class TestCustomUserManager:
    def test_create_user_success(self):
        user = User.objects.create_user(email='test@example.com', password='password123')
        assert user.email == 'test@example.com'
        assert user.check_password('password123')
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_no_email(self):
        with pytest.raises(ValueError, match='Email is required'):
            User.objects.create_user(email=None, password='password123')

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(email='admin@example.com', password='adminpassword')
        assert superuser.email == 'admin@example.com'
        assert superuser.check_password('adminpassword')
        assert superuser.is_active is True
        assert superuser.is_staff is True
        assert superuser.is_superuser is True

    def test_create_superuser_missing_is_staff(self):
        with pytest.raises(ValueError, match='Superuser must have is_staff=True.'):
            User.objects.create_superuser(email='admin@example.com', password='adminpassword', is_staff=False)

    def test_create_superuser_missing_is_superuser(self):
        with pytest.raises(ValueError, match='Superuser must have is_superuser=True.'):
            User.objects.create_superuser(email='admin@example.com', password='adminpassword', is_superuser=False)

