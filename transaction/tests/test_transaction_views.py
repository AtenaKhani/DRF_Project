import pytest
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings


pytestmark=pytest.mark.django_db

class TestRechargeWallet:
    endpoint=reverse('recharge-wallet')

    @patch('requests.post')
    def test__payment_request_with_valid_amount_success_and_return_302(self, mock_post, api_client, authenticated_user):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'code': 100, 'authority': '123456'},
            'errors': None
        }
        mock_post.return_value = mock_response
        url = self.endpoint
        response = api_client.post(url, {'amount': 10000})
        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == f"{settings.ZARINPAL_STARTPAY_URL}123456"

    @patch('requests.post')
    def test__payment_request_with_invalid_amount_rejected_and_return_400(self, mock_post, api_client, authenticated_user):
        url = self.endpoint
        response = api_client.post(url, {'amount': -100})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Amount must be positive.'

    @patch('requests.post')
    def test__payment_request_with_zero_amount_rejected_and_return_400(self, mock_post, api_client, authenticated_user):
        url = self.endpoint
        response = api_client.post(url, {'amount': 0})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Amount must be positive.'

    @patch('requests.post')
    def test__payment_request_failed_due_to_api_failure(self,mock_post, api_client, authenticated_user):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'code': -1, 'authority': '123456'},
            'errors': 'Payment failed'
        }
        mock_post.return_value = mock_response
        url = reverse('recharge-wallet')
        response = api_client.post(url, {'amount': 10000})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Payment request failed.'
        assert response.data['detail'] == 'Payment failed'

    @patch('requests.post')
    def test__payment_request_with_invalid_amount_rejected_and_return_400(self, mock_post, api_client, authenticated_user):
        url = reverse('recharge-wallet')
        response = api_client.post(url, {'amount': 'invalid'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Invalid amount.'

    def test__get_request_to_recharge_wallet_view_accepted_and_return_200(self, api_client, authenticated_user):
        url = self.endpoint
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Please provide the amount you want to charge your wallet.'


class  TestPaymentCallback:
    @patch('requests.post')
    def test_successful_payment_verification(self, mock_post, api_client, authenticated_user):
        # Set up mock response for the payment verification request
        mock_response = {
            'data': {
                'code': 100,
                'ref_id': 'TRANSACTION_ID'
            }
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        amount = 10.0
        api_client.session['payment_amount'] = amount
        api_client.session.save()#
        url = reverse('payment_callback')
        response = api_client.get(url, {'Authority': 'AUTHORITY_CODE', 'Status': 'OK'})
        print(response.content)
        assert response.status_code==200

        assert response.data['message'] == 'Payment successful.'
        assert response.data['transaction_id'] == 'TRANSACTION_ID'
        expected_balance = amount
        assert authenticated_user.wallet_balance, expected_balance

    @patch('requests.post')
    def test_payment_verification_fails_due_to_api_error(self, mock_post, api_client, authenticated_user):
        mock_response = {
            'data': {
                'code': 101,
                'errors': 'Some error'
            }
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        api_client.force_authenticate(user=authenticated_user)
        authenticated_user.wallet_balance = 0
        authenticated_user.save()
        response = api_client.get('/payment/callback/', {
            'Authority': 'AUTHORITY_CODE',
            'Status': 'OK'
        })
        authenticated_user.refresh_from_db()
        assert authenticated_user.wallet_balance == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Payment verification failed.'
        assert 'detail' in response.data

    @patch('requests.post')
    def test_payment_verification_fails_due_to_invalid_status(self, mock_post, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)
        authenticated_user.wallet_balance = 0
        authenticated_user.save()
        response = api_client.get('/payment/callback/', {
            'Authority': 'AUTHORITY_CODE',
            'Status': 'INVALID_STATUS'
        })
        authenticated_user.refresh_from_db()
        assert authenticated_user.wallet_balance == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Payment was not successful.'

