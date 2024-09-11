import pytest
from dj_rest_auth.views import LogoutView
from dj_rest_auth.registration.views import ResendEmailVerificationView
from django.urls import reverse, resolve
from users.views import  CustomRegisterView,CustomVerifyEmailView,CustomLoginView,UserProfileView,CustomPasswordChangeView

class TestUrl:
    def test__register_url(self):
            url = reverse('registration')
            resolver_match = resolve(url)
            assert resolver_match.view_name == 'registration'
            assert resolver_match.func.__name__ == CustomRegisterView.as_view().__name__


    def test__login_url(self):
            url = reverse('login')
            resolver_match = resolve(url)
            assert resolver_match.view_name == 'login'
            assert resolver_match.func.__name__ == CustomLoginView.as_view().__name__

    def test__logout_url(self):
        url = reverse('logout')
        resolver_match = resolve(url)
        assert resolver_match.view_name == 'logout'
        assert resolver_match.func.__name__ == LogoutView.as_view().__name__

    def test__profile_url(self):
        url = reverse('profile')
        resolver_match = resolve(url)
        assert resolver_match.view_name == 'profile'
        assert resolver_match.func.__name__ == UserProfileView.as_view().__name__

    def test__password_change_url(self):
        url = reverse('password_change')
        resolver_match = resolve(url)
        assert resolver_match.view_name == 'password_change'
        assert resolver_match.func.__name__ == CustomPasswordChangeView.as_view().__name__



    def test__verify_email_url(self):
        url = reverse('rest_verify_email')
        resolver_match = resolve(url)
        assert resolver_match.view_name == 'rest_verify_email'
        assert resolver_match.func.__name__ == CustomVerifyEmailView.as_view().__name__


    def test__resend_email_url(self):
        url = reverse('rest_resend_email')
        resolver_match = resolve(url)
        assert resolver_match.view_name == 'rest_resend_email'
        assert resolver_match.func.__name__ == ResendEmailVerificationView.as_view().__name__