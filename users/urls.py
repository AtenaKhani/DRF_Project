from django.urls import path, include, re_path
from .views import  CustomRegisterView,CustomVerifyEmailView,CustomLoginView
urlpatterns =[
   path('registration/', CustomRegisterView.as_view(), name='registration'),
   path('verify-email/', CustomVerifyEmailView.as_view(), name='rest_verify_email'),
   path('login/', CustomLoginView.as_view(), name='login'),
    re_path(
        r'^account-confirm-email/(?P<key>[-:\w]+)/$', CustomVerifyEmailView.as_view(),
        name='account_confirm_email',
    ),
    path(
        'account-email-verification-sent/', CustomVerifyEmailView.as_view(),
        name='account_email_verification_sent',
    ),
]
