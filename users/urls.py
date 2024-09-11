from dj_rest_auth.registration.views import ResendEmailVerificationView
from dj_rest_auth.views import LogoutView
from django.urls import path, include, re_path
from .views import  CustomRegisterView,CustomVerifyEmailView,CustomLoginView,UserProfileView,CustomPasswordChangeView

urlpatterns =[
   path('registration/', CustomRegisterView.as_view(), name='registration'),
   path('verify-email/', CustomVerifyEmailView.as_view(), name='rest_verify_email'),
   path('login/', CustomLoginView.as_view(), name='login'),
   path('profile/', UserProfileView.as_view(), name='profile'),
   path('logout/', LogoutView.as_view(), name='logout'),
   path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
   path('resend-email/', ResendEmailVerificationView.as_view(), name="rest_resend_email"),
    re_path(
        r'^account-confirm-email/(?P<key>[-:\w]+)/$', CustomVerifyEmailView.as_view(),
        name='account_confirm_email',
    ),
    path(
        'account-email-verification-sent/', CustomVerifyEmailView.as_view(),
        name='account_email_verification_sent',
    ),
]
