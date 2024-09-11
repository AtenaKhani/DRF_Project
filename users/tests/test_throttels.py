import os
import sys
import pytest
import requests_mock
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status


from  users.throttle import LoginRateThrottle

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
pytestmark=pytest.mark.django_db


# class TestLoginThrottle:
#
#
#     @patch('django_redis.cache.RedisCache.get')
#     @patch('django_redis.cache.RedisCache.set')
#     @patch('django_redis.cache.RedisCache.ttl')
#     def test_login_rate_limiting_for_anonymous_user(self,mock_ttl, mock_set, mock_get, api_client):
#         mock_get.side_effect = list(range(6))
#         mock_set.return_value = True
#         mock_ttl.return_value = 10
#         url = reverse('login')
#         request_count = 0
#         with requests_mock.Mocker() as mock:
#             mock.post(url, text='mocked response')
#             for i in range(6):
#                 response = api_client.post(url, {'email': 'test_email', 'password': 'testpassword'}, format='json')
#                 if request_count < 5:
#                     assert response.status_code == status.HTTP_400_BAD_REQUEST
#                 else:
#                     assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
#                 request_count += 1
#
#
#
#     @patch('django_redis.cache.RedisCache.get')
#     @patch('django_redis.cache.RedisCache.set')
#     @patch('django_redis.cache.RedisCache.ttl')
#     def test_login_rate_limiting_for_authenticated_user(self,mock_ttl, mock_set, mock_get, api_client,user_instance):
#         mock_get.side_effect = list(range(21))
#         mock_set.return_value = True
#         mock_ttl.return_value = 10
#         url = reverse('login')
#         api_client.force_authenticate(user=user_instance)
#
#         request_count = 0
#         with requests_mock.Mocker() as mock:
#             mock.post(url, text='mocked response')
#             for i in range(21):
#                 response = api_client.post(url, {'email': 'test_email', 'password': 'testpassword'}, format='json')
#                 if request_count < 20:
#                     assert response.status_code == status.HTTP_400_BAD_REQUEST
#                 else:
#                     assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
#                 request_count += 1

