import pytest

from django.urls import reverse,resolve

from transaction.views import  RechargeWalletView,PaymentCallbackView

class TestUrl:
    def test__payment_request_url(self):
            url = reverse('recharge-wallet')
            resolver_match = resolve(url)
            assert resolver_match.view_name == 'recharge-wallet'
            assert resolver_match.func.__name__ == RechargeWalletView.as_view().__name__

    def test__payment_callback_url(self):
            url = reverse('payment_callback')
            resolver_match = resolve(url)
            assert resolver_match.view_name == 'payment_callback'
            assert resolver_match.func.__name__ == PaymentCallbackView.as_view().__name__



