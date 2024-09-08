import requests
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

class RechargeWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Please provide the amount you want to charge your wallet.'
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        amount = float(amount)
        try:
            if amount <= 0:
                    return Response({'error': 'Amount must be positive.'}, status=status.HTTP_400_BAD_REQUEST)

            request.session['payment_amount'] = int(amount)

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
            else:
                print(f"Error: {response.status_code}, {response.text}")
            if response_data.get('data') and response_data['data'].get('code') == 100:
                    payment_url = f"{settings.ZARINPAL_STARTPAY_URL}{response_data['data']['authority']}"
                    # return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
                    return redirect(payment_url)
            else:
                    return Response({'error': 'Payment request failed.', 'detail': response_data.get('errors')}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid amount.'}, status=status.HTTP_400_BAD_REQUEST)
class PaymentCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        authority = request.GET.get('Authority')
        user = request.user
        amount = request.session.get('payment_amount', 0)

        if status == 'OK' and amount:
            payment_verification_data = {
                'merchant_id': settings.ZARINPAL_MERCHANT_ID,
                'amount': int(amount * 10),
                'authority': authority,

            }
            response = requests.post(settings.ZARINPAL_VERIFY_URL, json=payment_verification_data)
            response_data = response.json()

            if response_data.get('data') and response_data['data'].get('code') == 100:
                transaction_id = response_data['data'].get('ref_id', 'No transaction ID available')
                user.wallet_balance += amount
                user.save()
                return Response({'message': 'Payment successful.', 'transaction_id': transaction_id}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Payment verification failed.', 'detail': response_data.get('errors')},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Payment was not successful.'}, status=status.HTTP_400_BAD_REQUEST)