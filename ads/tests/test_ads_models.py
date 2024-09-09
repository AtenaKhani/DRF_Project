import pytest

class TestCarModel:
    @pytest.mark.django_db
    def test__test_car_access(self,car_instance):
        print(car_instance)

class TestAdModel:
    @pytest.mark.django_db
    def test__test_ad_access(self,ad_instance):
        print(ad_instance)