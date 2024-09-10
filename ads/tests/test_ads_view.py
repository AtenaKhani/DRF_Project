import pytest
from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.saml.conftest import client

from django.shortcuts import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_jwt.settings import api_settings

from ads.models  import Car,Ad
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark=pytest.mark.django_db


class TestAdList:
    endpoint=reverse('ads:ad_list')
    client = APIClient()
    def test__unauthenticated_request_should_be_accepted_and_return_200(self):
        url=self.endpoint
        response=self.client.get(url)
        assert response.status_code ==status.HTTP_200_OK
    def test__authenticated_request_should_be_accepted_and_return_200(self,user_instance):
        url=self.endpoint
        self.client.force_authenticate(user=user_instance)
        response=self.client.get(url)
        assert response.status_code ==status.HTTP_200_OK
    def test__authenticated_request_return_all_ads_200(self,user_instance,ad_instance,ad_instance2):
        url=self.endpoint
        self.client.force_authenticate(user=user_instance)
        response = self.client.get(url)
        response_json = response.json()
        total_ads = Ad.objects.all().count()
        ad_list = [result['id'] for result in response_json['results']]
        assert isinstance(response_json,dict)
        assert(len(response_json['results']) > 0)
        assert  len(ad_list)==total_ads
    def test__unauthenticated_request_return_all_ads_200(self,user_instance,ad_instance,ad_instance2):
        url=self.endpoint
        response = self.client.get(url)
        response_json = response.json()
        total_ads = Ad.objects.all().count()
        ad_list = [result['id'] for result in response_json['results']]
        assert isinstance(response_json,dict)
        assert(len(response_json['results']) > 0 )
        assert len(ad_list) == total_ads

    def test__required_fields_in_ad_list(self,ad_instance):
        response = self.client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        for item in response.data['results']:
            assert 'car_title' in item
            assert 'car_year' in item
            assert 'location' in item
            assert 'price' in item
            assert 'payment_method' in item
            assert 'car_image' in item
            assert 'is_premium' in item

        for item in response.data['results']:
            assert 'description' not in item

    def test__search_by_title(self,ad_instance):
        response = self.client.get(self.endpoint, {'search': 'Toyota'})
        assert response.status_code == status.HTTP_200_OK
        for item in response.data['results']:
            assert 'Toyota' in item['car_title']

    def test__search_by_location(self,ad_instance):
        response = self.client.get(self.endpoint, {'search': 'Tehran'})
        for item in response.data['results']:
            assert 'Tehran' in item['location']

    def test__filter_by_has_image(self,ad_instance):
        response = self.client.get(self.endpoint, {'car__image': 'true'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        for result in results:
            assert (result['car_image'] != None)
    def test__filter_by_year(self,ad_instance):
        response = self.client.get(self.endpoint, {'car__year': 1400})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.car.year ==1400

    def test__filter_by_transmission(self, ad_instance):
        response = self.client.get(self.endpoint, {'car__transmission': 'automatic'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.car.transmission == "automatic"

    def test__filter_by_body_type(self, ad_instance):
        response = self.client.get(self.endpoint, {'car__body_type': 'passenger_car'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.car.body_type == "passenger_car"

    def test__filter_by_fuel(self, ad_instance):
        response = self.client.get(self.endpoint, {'car__fuel': 'gasoline'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.car.fuel == "gasoline"

    def test__filter_by_has_price(self, ad_instance):
        response = self.client.get(self.endpoint, {'price': 'true'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        for result in results:
            assert (result['price'] > 0)

    def test__filter_by_payment_method(self, ad_instance):
        response = self.client.get(self.endpoint, {'payment_method': 'lumpsum'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        for result in results:
            assert (result['payment_method']=="lumpsum")
    def test__filter_by_type(self, ad_instance):
        response = self.client.get(self.endpoint, {'type': 'free'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        for result in results:
            assert (result['is_premium'] == 0)

class TestAdDetail:
    client = APIClient()
    def test__unauthenticated_request_should_be_accepted_and_return_200(self,ad_instance):
        url = reverse('ads:ad_detail', args=[ad_instance.pk])
        response=self.client.get(url)
        assert response.status_code ==status.HTTP_200_OK
    def test__authenticated_request_should_be_accepted_and_return_200(self,user_instance,ad_instance):
        url = reverse('ads:ad_detail', args=[ad_instance.pk])
        self.client.force_authenticate(user=user_instance)
        response=self.client.get(url)
        assert response.status_code ==status.HTTP_200_OK

    def test__ad_detail_returns_correct_data(self,ad_instance,expected_data):
        url = reverse('ads:ad_detail', args=[ad_instance.pk])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for key, value in expected_data.items():
            if isinstance(value, dict):
                for car_key, car_value in value.items():
                    assert response.data['car'][car_key] == car_value
            else:
                assert response.data[key] == value
    def test__ad_detail_returns_only_one_ads(self,ad_instance):
        url = reverse('ads:ad_detail', args=[ad_instance.pk])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data,dict)
class TestUserAdList:
    endpoint = reverse('ads:my_ads')
    client = APIClient()


    def test__request_with_valid_jwt_token_should_be_accepted_and_return_200(self,user_instance,ad_instance):
        url = self.endpoint
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        self.client.credentials( HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert  len(response.data['results'] ) > 0

    def test__request_with_invalid_jwt_token_should_be_rejected_and_return_401(self,user_instance,ad_instance):
        url = self.endpoint
        access_token = 'invalid_token'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == "Given token not valid for any token type"

    def test__unauthenticated_request_should_be_rejected_and_return_401(self):
        url=self.endpoint
        client = APIClient()
        response=client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail']== 'Authentication credentials were not provided.'
    def test__all_ads_belong_to_user(self,user_instance,ad_instance):
        url = self.endpoint
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.user==user_instance
    def test__retrieves_all_own_advertisements_only(self,user_instance,ad_instance,ad_instance2):
        url = self.endpoint
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        results = response.data['results']
        total_user_ads = Ad.objects.filter(user=user_instance).count()
        ad_list = [result['id'] for result in results]
        retrieved_ads =len(ad_list)
        assert retrieved_ads == total_user_ads
class TestUserAdDetail:
    client = APIClient()
    def test__request_with_valid_jwt_token_should_be_accepted_and_return_200(self,user_instance,ad_instance):
        url = reverse('ads:detail_my_ad',args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        self.client.credentials( HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test__request_with_invalid_jwt_token_should_be_rejected_and_return_401(self,user_instance,ad_instance):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        access_token = 'invalid_token'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == "Given token not valid for any token type"

    def test__unauthenticated_request_should_be_rejected_and_return_401(self,ad_instance):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        client = APIClient()
        response=client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail']== 'Authentication credentials were not provided.'
    def test__ad_detail_returns_correct_data(self,user_instance,ad_instance,new_ad):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for key, value in new_ad.items():
            if isinstance(value, dict):
                for car_key, car_value in value.items():
                    assert response.data['car'][car_key] == car_value
            else:
                assert response.data[key] == value
    def test__ad_detail_returns_only_one_ads(self,user_instance,ad_instance):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data,dict)













