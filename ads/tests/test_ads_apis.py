import pytest

from django.shortcuts import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


from ads.models  import Car,Ad


pytestmark=pytest.mark.django_db


class TestAdList:
    endpoint=reverse('ads:ad_list')
    def test__unauthenticated_request_should_be_accepted_and_return_200(self,api_client):
        url=self.endpoint
        response=api_client.get(url)
        assert response.status_code ==status.HTTP_200_OK

    def test__authenticated_request_should_be_accepted_and_return_200(self,api_client,user_instance):
        url=self.endpoint
        api_client.force_authenticate(user=user_instance)
        response=api_client.get(url)
        assert response.status_code ==status.HTTP_200_OK

    def test__authenticated_request_return_all_ads_200(self,api_client,user_instance,ad_instance):
        url=self.endpoint
        api_client.force_authenticate(user=user_instance)
        response = api_client.get(url)
        response_json = response.json()
        total_ads = Ad.objects.all().count()
        ad_list = [result['id'] for result in response_json['results']]
        assert isinstance(response_json,dict)
        assert(len(response_json['results']) > 0)
        assert  len(ad_list)==total_ads

    def test__unauthenticated_request_return_all_ads_200(self,api_client,user_instance,ad_instance):
        url=self.endpoint
        response = api_client.get(url)
        response_json = response.json()
        total_ads = Ad.objects.all().count()
        ad_list = [result['id'] for result in response_json['results']]
        assert isinstance(response_json,dict)
        assert(len(response_json['results']) > 0 )
        assert len(ad_list) == total_ads

    def test__required_fields_in_ad_list(self,api_client,ad_instance):
        response = api_client.get(self.endpoint)
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

    def test__search_by_title(self,api_client,ad_instance):
        response = api_client.get(self.endpoint, {'search': 'Toyota'})
        assert response.status_code == status.HTTP_200_OK
        for item in response.data['results']:
            assert 'Toyota' in item['car_title']

    def test__search_by_location(self,api_client,ad_instance):
        response = api_client.get(self.endpoint, {'search': 'Tehran'})
        for item in response.data['results']:
            assert 'Tehran' in item['location']

    def test__filter_by_has_image(self,api_client,ad_instance):
        response = api_client.get(self.endpoint, {'car__image': 'true'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        for result in results:
            assert (result['car_image'] != None)
    def test__filter_by_year(self,api_client,ad_instance):
        response = api_client.get(self.endpoint, {'car__year': 1400})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.car.year ==1400

    def test__filter_by_transmission(self,api_client, ad_instance):
        response = api_client.get(self.endpoint, {'car__transmission': 'automatic'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.car.transmission == "automatic"

    def test__filter_by_body_type(self,api_client, ad_instance):
        response = api_client.get(self.endpoint, {'car__body_type': 'passenger_car'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.car.body_type == "passenger_car"

    def test__filter_by_fuel(self,api_client, ad_instance):
        response = api_client.get(self.endpoint, {'car__fuel': 'gasoline'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.car.fuel == "gasoline"

    def test__filter_by_has_price(self,api_client, ad_instance):
        response = api_client.get(self.endpoint, {'price': 'true'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        for result in results:
            assert (result['price'] > 0)

    def test__filter_by_payment_method(self, api_client,ad_instance):
        response = api_client.get(self.endpoint, {'payment_method': 'lumpsum'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        for result in results:
            assert (result['payment_method']=="lumpsum")

    def test__filter_by_type(self,api_client, ad_instance):
        response = api_client.get(self.endpoint, {'type': 'free'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        for result in results:
            assert (result['is_premium'] == 0)

class TestAdDetail:
    def test__unauthenticated_request_should_be_accepted_and_return_200(self,api_client,ad_instance):
        url = reverse('ads:ad_detail', args=[ad_instance.pk])
        response=api_client.get(url)
        assert response.status_code ==status.HTTP_200_OK

    def test__authenticated_request_should_be_accepted_and_return_200(self,api_client,user_instance,ad_instance):
        url = reverse('ads:ad_detail', args=[ad_instance.pk])
        api_client.force_authenticate(user=user_instance)
        response=api_client.get(url)
        assert response.status_code ==status.HTTP_200_OK

    def test__ad_detail_returns_correct_data(self,api_client,ad_instance,expected_data):
        url = reverse('ads:ad_detail', args=[ad_instance.pk])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for key, value in expected_data.items():
            if isinstance(value, dict):
                for car_key, car_value in value.items():
                    assert response.data['car'][car_key] == car_value
            else:
                assert response.data[key] == value

    def test__ad_detail_returns_only_one_ads(self,api_client,ad_instance):
        url = reverse('ads:ad_detail', args=[ad_instance.pk])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data,dict)
class TestUserAdList:
    endpoint = reverse('ads:my_ads')
    def test__request_with_valid_jwt_token_should_be_accepted_and_return_200(self,api_client,user_instance,ad_instance):
        url = self.endpoint
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials( HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert  len(response.data['results'] ) > 0

    def test__request_with_invalid_jwt_token_should_be_rejected_and_return_401(self,api_client,user_instance):
        url = self.endpoint
        access_token = 'invalid_token'
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == "Given token not valid for any token type"

    def test__unauthenticated_request_should_be_rejected_and_return_401(self,api_client):
        url=self.endpoint
        response=api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail']== 'Authentication credentials were not provided.'
    def test__all_ads_belong_to_user(self,api_client,user_instance,ad_instance):
        url = self.endpoint
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        results = response.data['results']
        ad_ids = [result['id'] for result in results]
        for ad_id in ad_ids:
            ad = Ad.objects.get(id=ad_id)
            assert ad.user==user_instance

    def test__retrieves_all_own_advertisements_only(self,api_client,user_instance,ad_instance):
        url = self.endpoint
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        results = response.data['results']
        total_user_ads = Ad.objects.filter(user=user_instance).count()
        ad_list = [result['id'] for result in results]
        retrieved_ads =len(ad_list)
        assert retrieved_ads == total_user_ads


class TestUserAdDetail:
    def test__request_with_valid_jwt_token_should_be_accepted_and_return_200(self,api_client,user_instance,ad_instance):
        url = reverse('ads:detail_my_ad',args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials( HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test__request_with_invalid_jwt_token_should_be_rejected_and_return_401(self,api_client,user_instance,ad_instance):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        access_token = 'invalid_token'
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == "Given token not valid for any token type"

    def test__unauthenticated_request_should_be_rejected_and_return_401(self,api_client,ad_instance):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        response=api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail']== 'Authentication credentials were not provided.'

    def test__put_request_with_unauthenticated_user_should_be_rejected_and_return_401(self,api_client,ad_instance,new_ad):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        response = api_client.put(url, data=new_ad, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == 'Authentication credentials were not provided.'


    def test__put_request_with_invalid_jwt_token_should_be_rejected_and_return_401(self,api_client,user_instance,new_ad,ad_instance):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        access_token = 'invalid_token'
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.put(url, data=new_ad, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == "Given token not valid for any token type"

    def test__ad_detail_returns_correct_data(self,api_client,user_instance,ad_instance,new_ad):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for key, value in new_ad.items():
            if isinstance(value, dict):
                for car_key, car_value in value.items():
                    assert response.data['car'][car_key] == car_value
            else:
                assert response.data[key] == value

    def test__ad_detail_returns_only_one_ads(self,api_client,user_instance,ad_instance):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data,dict)


    def test__user_wallet_balance_unchanged_in_update_ad_with_unchanged_type(self,api_client,user_instance,ad_instance,new_ad):
        initial_balance=user_instance.wallet_balance
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.put(url, data=new_ad, format='json')
        user_instance.refresh_from_db()
        final_balance=user_instance.wallet_balance
        assert response.status_code == status.HTTP_200_OK
        assert initial_balance == final_balance
    def test__user_wallet_balance_changed_in_update_ad_with_changed_type_to_premium(self,api_client,user_instance,ad_instance,new_ad):
        new_ad['type'] = 'premium'
        user_instance.wallet_balance = 60000
        user_instance.save()
        initial_balance=user_instance.wallet_balance
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.put(url, data=new_ad, format='json')
        user_instance.refresh_from_db()
        final_balance=user_instance.wallet_balance
        assert response.status_code == status.HTTP_200_OK
        assert initial_balance != final_balance

    def test__error_to_update_add_free_from_premium(self,api_client,new_ad,ad_instance,user_instance):
        new_ad['type'] = 'free'
        ad_instance.type ='premium'
        ad_instance.save()
        initial_balance = user_instance.wallet_balance
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.put(url, data=new_ad, format='json')
        user_instance.refresh_from_db()
        final_balance = user_instance.wallet_balance
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert initial_balance == final_balance
        assert response.data[0] == "You cannot change the premium ad to free"

    def test__put_request_to_updeta_ad_with_valid_data_accepted_and_return_200(self,api_client,new_ad,ad_instance,user_instance):
        new_ad['price'] = 300000
        new_ad['car']['year'] =2021
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.put(url, data=new_ad, format='json')
        ad_instance.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data['price'] ==300000
        assert ad_instance.price == 300000
        assert response.data['car']['year'] ==2021
        assert ad_instance.car.year == 2021

    def test__put_request_to_update_ad_with_invalid_year_and_price_and_types_rejected_and_return_400(self,api_client,invalid_new_ad,ad_instance,user_instance):
        url = reverse('ads:detail_my_ad', args=[ad_instance.pk])
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.put(url, data=invalid_new_ad, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['price'][0] == 'Price cannot be negative.'
        assert response.data['car']['year'][0] == 'Miladi year must be between 1970 and the current year.'
        assert response.data['type'][0] == 'Your wallet balance is less than 50000 Tomans, you cannot register a premium ad'





class TestAdCreate:
    endpoint=reverse('ads:create_ad')

    def test__get_request_with_valid_jwt_token_returns_method_not_allowed_405(self,api_client, user_instance):
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert  response.data['detail'] == "Method \"GET\" not allowed."

    def test__request_with_valid_jwt_token_should_be_rejected_and_return_401(self, api_client,user_instance):
        access_token = 'invalid_token'
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == "Given token not valid for any token type"

    def test__request_with_unauthenticated_user_should_be_rejected_and_return_401(self,api_client):
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    def test__post_request_by_user_with_valid_jwt_token_and_without_phone_number_rejected_and_returns_400(self,api_client,user_without_phone_number,new_ad):
        refresh = RefreshToken.for_user(user_without_phone_number)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.post(self.endpoint,new_ad, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert  response.data['detail'] == "Please go to your profile and provide your phone number before posting an ad."

    def test__post_request_to_create_ad_with_valid_data_by_user_with_phone_accepted_and_return_201(self,api_client,user_instance,new_ad):
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.post(self.endpoint, new_ad, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == "Car and Ad created successfully"

    def test__post_request_to_create_ad_with_invalid_year_and_price_and_types_by_user_with_phone_rejected_and_return_400(self,api_client,user_instance,invalid_new_ad):
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.post(self.endpoint, invalid_new_ad, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['price'][0] == 'Price cannot be negative.'
        assert response.data['car']['year'][0] == 'Miladi year must be between 1970 and the current year.'
        assert response.data['type'][0] =='Your wallet balance is less than 50000 Tomans, you cannot register a premium ad'




