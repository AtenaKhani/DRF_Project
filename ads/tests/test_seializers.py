import re
from unittest.mock import Mock

import pytest
from django.core.serializers import serialize

from django.urls import reverse

from rest_framework.exceptions import ValidationError

from ads.serializers import CarSerializer,AdListSerializer,AdCreateSerializer
from ads.models import Ad,Car


pytestmark=pytest.mark.django_db

class TestCarSerializer:
    car= {'title':'saman', 'year':1400,'mileage':'2000','body_color':'black','inside_color':'black','transmission':'automatic','fuel':'gasoline'}
    def test__validate_year_with_valid_shamsi_year(self):
        serializer = CarSerializer(data=self.car)
        assert serializer.is_valid()
        assert serializer.validated_data['year'] == 1400

    def test__validate_year_with_valid_miladi_year(self):
        self.car['year']=2023
        serializer = CarSerializer(data=self.car)
        assert serializer.is_valid()
        assert serializer.validated_data['year'] == 2023



    def test__validate_year_with_invalid_shamsi_year(self):
        self.car['year'] = 1501
        serializer = CarSerializer(data=self.car)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test__validate_year_with_invalid_miladi_year(self):
        self.car['year'] = 2070
        serializer = CarSerializer(data=self.car)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)




class TestAdListSerializer:
    def test__get_is_premium(self,ad_instance):
        serializer = AdListSerializer(ad_instance)
        data = serializer.data
        assert data['is_premium'] is False
    def test__get_car_year(self,ad_instance):
        serializer = AdListSerializer(ad_instance)
        data = serializer.data
        assert data['car_year'] == ad_instance.car.year

    def test__get_car_title(self,ad_instance):
        serializer = AdListSerializer(ad_instance)
        data = serializer.data
        assert data['car_title'] == ad_instance.car.title

    def test__get_car_image(self,ad_instance):
        serializer = AdListSerializer(ad_instance)
        data = serializer.data
        assert data['car_image'] == ad_instance.car.image


class TestAdCreateSerializer:
    def test__validate_price_with_invalid_data(self,new_ad,user_instance):
        new_ad['price'] = -100000
        serializer=AdCreateSerializer(data=new_ad,context={'request': Mock(user=user_instance)})
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test__validate_price_with_valid_data(self, new_ad, user_instance):
        new_ad['price'] = +100000
        serializer = AdCreateSerializer(data=new_ad, context={'request': Mock(user=user_instance)})
        assert serializer.is_valid()
        assert serializer.validated_data['price'] == 100000

    def test__validate_type_with_insufficient_wallet_balance(self, new_ad, user_instance):
            user_instance.wallet_balance = 6000
            new_ad['type'] = 'premium'
            serializer = AdCreateSerializer(data=new_ad, context={'request': Mock(user=user_instance)})
            with pytest.raises(ValidationError):
                serializer.is_valid(raise_exception=True)

    def test__validate_type_with_sufficient_wallet_balance(self,new_ad,user_instance):
        user_instance.wallet_balance = 60000
        new_ad['type'] = 'premium'
        serializer = AdCreateSerializer(data=new_ad, context={'request': Mock(user=user_instance)})
        assert serializer.is_valid()
        assert serializer.validated_data['type'] == 'premium'


    def test__generate_ad_code(self):
        serializer = AdCreateSerializer()
        ad_code = serializer.generate_ad_code()
        pattern = r'^myad-\d{8}-[A-Z0-9]{8}$'
        assert re.match(pattern, ad_code), f"Ad code {ad_code} does not match the expected format"

    def test__success_create_free_ad_with_valid_data(self,new_ad,user_instance):
        serializer = AdCreateSerializer(data=new_ad, context={'request' : Mock(user=user_instance)})
        assert serializer.is_valid(), serializer.errors
        ad =  serializer.save()
        assert Ad.objects.count() == 1
        assert Car.objects.count() == 1
        assert ad.user == user_instance
        assert ad.car.title == new_ad['car']['title']
        assert ad.code is not None
        assert ad.type == new_ad['type']
        assert ad.url == reverse('ads:ad_detail', args=[ad.pk])

    def test__user_wallet_balance_unchanged_in_create_free_ad(self,new_ad, user_instance):
        initial_balance = user_instance.wallet_balance
        serializer = AdCreateSerializer(data=new_ad, context={'request': Mock(user=user_instance)})
        assert serializer.is_valid(), serializer.errors
        assert serializer.save()
        user_instance.refresh_from_db()
        assert user_instance.wallet_balance == initial_balance

    def test__success_create_premium_ad_with_valid_data(self, new_ad, user_instance):
        user_instance.wallet_balance = 60000
        new_ad['type']='premium'
        serializer = AdCreateSerializer(data=new_ad, context={'request': Mock(user=user_instance)})
        assert serializer.is_valid(), serializer.errors
        ad = serializer.save()
        assert Ad.objects.count() == 1
        assert Car.objects.count() == 1
        assert ad.user == user_instance
        assert ad.car.title == new_ad['car']['title']
        assert ad.code is not None
        assert ad.type == new_ad['type']
        assert ad.url == reverse('ads:ad_detail', args=[ad.pk])

    def test__user_wallet_balance_changed_in_create_premium_ad(self,new_ad, user_instance):
        user_instance.wallet_balance = 60000
        new_ad['type'] = 'premium'

        serializer = AdCreateSerializer(data=new_ad, context={'request': Mock(user=user_instance)})
        assert serializer.is_valid(), serializer.errors
        assert serializer.save()
        user_instance.refresh_from_db()
        assert user_instance.wallet_balance != 60000
        assert user_instance.wallet_balance == 10000

    def test__success_update_ad_with_valid_data(self,new_ad,user_instance,ad_instance):
        serializer = AdCreateSerializer(instance=ad_instance, data=new_ad,
                                        context={'request': Mock(user=user_instance)})

        assert serializer.is_valid(), serializer.errors
        ad =  serializer.save()
        assert Ad.objects.count() == 1
        assert Car.objects.count() == 1
        assert ad.user == user_instance
        assert ad.car.title == new_ad['car']['title']
        assert ad.price == new_ad['price']
        assert ad.code is not None
        assert ad.type == new_ad['type']
        assert ad.location == new_ad['location']

    def test__user_wallet_balance_changed_in_update_ad_to_premium(self, ad_instance, user_instance,new_ad):
        new_ad['type'] = 'premium'
        user_instance.wallet_balance = 60000
        ad_instance.type = 'free'
        ad_instance.save()
        serializer = AdCreateSerializer(instance=ad_instance, data=new_ad,
                                        context={'request': Mock(user=user_instance)})

        assert serializer.is_valid(), serializer.errors
        ad = serializer.save()
        user_instance.refresh_from_db()
        assert ad.type == 'premium'
        assert user_instance.wallet_balance == 10000

    def test__user_wallet_balance_unchanged_in_update_ad_with_no_change_in_type(self, ad_instance, user_instance, new_ad):
        new_ad['type'] = 'free'
        user_instance.wallet_balance = 60000
        user_instance.save()
        ad_instance.type = 'free'
        ad_instance.save()
        serializer = AdCreateSerializer(instance=ad_instance, data=new_ad,
                                        context={'request': Mock(user=user_instance)})

        assert serializer.is_valid(), serializer.errors
        ad = serializer.save()
        user_instance.refresh_from_db()
        assert ad.type == 'free'
        assert user_instance.wallet_balance == 60000









