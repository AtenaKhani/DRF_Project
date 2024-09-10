import requests
import logging

from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger('transaction')


class RechargeWalletView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Please provide the amount you want to charge your wallet.'
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        try:
            amount = float(amount)
            if amount <= 0:
                    return Response({'error': 'Amount must be positive.'}, status=status.HTTP_400_BAD_REQUEST)

            request.session['payment_amount'] = int(amount)
            request.session.save()

            logger.info(f"User {request.user.email} requested to charge {amount}.")

            payment_data = {
                    'merchant_id': settings.ZARINPAL_MERCHANT_ID,
                     #Convert to Rial
                    'amount': int(amount * 10),
                    'callback_url': request.build_absolute_uri('/payment/callback/'),
                    'description': 'Payment for order',
            }



            response = requests.post(settings.ZARINPAL_REQUEST_URL, json=payment_data)
            if response.status_code == 200:
                response_data = response.json()
                logger.info(
                    f"Payment request sent successfully for user {request.user.email}. Response: {response_data}")
            else:
                logger.error(
                    f"Error in payment request for user {request.user.email}: {response.status_code}, {response.text}")
            if response_data.get('data') and response_data['data'].get('code') == 100:
                    payment_url = f"{settings.ZARINPAL_STARTPAY_URL}{response_data['data']['authority']}"
                    logger.info(f"Payment URL generated for user {request.user.email}: {payment_url}")
                    # return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
                    return redirect(payment_url)
            else:
                logger.error(
                    f"Payment request failed for user {request.user.email}. Errors: {response_data.get('errors')}")

                return Response({'error': 'Payment request failed.', 'detail': response_data.get('errors')}, status=status.HTTP_400_BAD_REQUEST)

        except (ValueError, TypeError):
            return Response({'error': 'Invalid amount.'}, status=status.HTTP_400_BAD_REQUEST)
class PaymentCallbackView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        authority = request.GET.get('Authority')
        payment_status = request.GET.get('Status')
        user = request.user
        amount=10
        # amount = request.GET.get('Amount')

        if payment_status == 'OK' and amount:
            payment_verification_data = {
                'merchant_id': settings.ZARINPAL_MERCHANT_ID,
                'amount': int(amount * 10),
                'authority': authority,
            }
            response = requests.post(settings.ZARINPAL_VERIFY_URL, json=payment_verification_data)
            response_data = response.json()
            logger.info(f"Payment verification response: {response_data}")

            if response_data.get('data') and response_data['data'].get('code') == 100:
                transaction_id = response_data['data'].get('ref_id', 'No transaction ID available')
                user.wallet_balance += amount
                user.save()
                logger.info(f"Payment successful for user {user.email}. Transaction ID: {transaction_id}. Wallet balance updated.")
                return Response({'message': 'Payment successful.', 'transaction_id': transaction_id}, status=status.HTTP_200_OK)
            else:
                logger.error(f"Payment verification failed for user {user.email}. Errors: {response_data.get('errors')}")
                return Response({'error': 'Payment verification failed.', 'detail': response_data.get('errors')},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.warning(f"Payment was not successful for user {user.email}. Status: {payment_status}, Amount: {amount}")
            return Response({'error': 'Payment was not successful.'}, status=status.HTTP_400_BAD_REQUEST)
