import pytest
from rest_framework.exceptions import ValidationError
from ads.serializers import CarSerializer,AdListSerializer
pytestmark=pytest.mark.django_db

class TestCarSerializer:
    car= {'title':'saman', 'year':1400,'mileage':'2000','body_color':'black','inside_color':'black','transmission':'automatic','fuel':'gasoline'}
    def test_validate_year_with_valid_shamsi_year(self):
        serializer = CarSerializer(data=self.car)
        assert serializer.is_valid()
        assert serializer.validated_data['year'] == 1400

    def test_validate_year_with_valid_miladi_year(self):
        self.car['year']=2023
        serializer = CarSerializer(data=self.car)
        assert serializer.is_valid()
        assert serializer.validated_data['year'] == 2023


    def test_validate_year_with_invalid_shamsi_year(self):
        self.car['year'] = 1501
        serializer = CarSerializer(data=self.car)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_year_with_invalid_miladi_year(self):
        self.car['year'] = 2070
        serializer = CarSerializer(data=self.car)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestAdListSerializer:
    def test_get_is_premium(self,ad_instance):
        serializer = AdListSerializer(ad_instance)
        data = serializer.data
        assert data['is_premium'] is False

    def test_get_car_year(self,ad_instance):
        serializer = AdListSerializer(ad_instance)
        data = serializer.data
        assert data['car_year'] == ad_instance.car.year

    def test_get_car_title(self,ad_instance):
        serializer = AdListSerializer(ad_instance)
        data = serializer.data
        assert data['car_title'] == ad_instance.car.title

    def test_get_car_image(self,ad_instance):
        serializer = AdListSerializer(ad_instance)
        data = serializer.data
        assert data['car_image'] == ad_instance.car.image
