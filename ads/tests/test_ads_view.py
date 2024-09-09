import pytest

from django.shortcuts import reverse

from rest_framework import status
from rest_framework.test import APIClient

from ads.models  import Car,Ad

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
    def test__authenticated_request_return_all_ads_200(self,user_instance,ad_instance):
        url=self.endpoint
        self.client.force_authenticate(user=user_instance)
        response = self.client.get(url)
        response_json = response.json()
        assert isinstance(response_json,dict)
        assert(len(response_json['results']) > 0)
    def test__unauthenticated_request_return_all_ads_200(self,user_instance,ad_instance):
        url=self.endpoint
        response = self.client.get(url)
        response_json = response.json()
        assert isinstance(response_json,dict)
        assert(len(response_json['results']) > 0 )

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
    def test_ad_detail_returns_only_one_ads(self,ad_instance):
        url = reverse('ads:ad_detail', args=[ad_instance.pk])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data,dict)











