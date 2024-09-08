from django.urls import path
from .views import RechargeWalletView, PaymentCallbackView

urlpatterns = [
    path('wallet/recharge/', RechargeWalletView.as_view(), name='recharge-wallet'),
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment_callback'),
]
