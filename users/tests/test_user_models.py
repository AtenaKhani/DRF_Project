import pytest

class TestAdModel:
    @pytest.mark.django_db
    def test__test_user_access(self,user_instance):
        print(user_instance)