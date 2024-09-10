import pytest

from django.contrib.auth import get_user_model
from datetime import date

from ads.models import Car,Ad



User= get_user_model()

@pytest.fixture
def car_instance():
    return Car.objects.create(
        title = "Toyota Corolla",
        year = 2020,
        mileage = "20000",
        body_color = "red",
        inside_color = "black",
        body_type ='passenger_car',
        transmission ="automatic" ,
        fuel = "gasoline",
        image = "https://images.app.goo.gl/JVy5hXzcpjAvm72XA"
    )
@pytest.fixture
def user_instance():
    return User.objects.create_user(
        email = "aakhani@gmail.com",
        first_name = "amir",
        last_name = "khani",
        phone_number = "+989387619549",
        birth_date = date(1990, 1, 1),
        is_active = True,
        is_staff = False,
        wallet_balance = 50000.00

    )

@pytest.fixture
def ad_instance(car_instance,user_instance):
    return Ad.objects.create(
        code = "myad-20240907-U5F1YOYH",
        user = user_instance,
        car = car_instance,
        description = "Immediate sale",
        location = "Tehran",
        price = 5000000000,
        payment_method = "lumpsum",
        seller_contact = "https://bama.ir/dealer/5904",
        url = "https://bama.ir/car/detail-7chjai4l-fownix-arrizo6pro-1403",
        type = "free"

    )
@pytest.fixture
def user_instance2():
    return User.objects.create_user(
        email = "aaakhani@gmail.com",
        first_name = "amiri",
        last_name = "khani",
        phone_number = "+989387619549",
        birth_date = date(1990, 1, 1),
        is_active = True,
        is_staff = False,
        wallet_balance = 50000.00

    )
@pytest.fixture
def ad_instance2(car_instance2,user_instance2):
    return Ad.objects.create(
        code = "myad-20240907-U5F1YOYH22",
        user = user_instance2,
        car = car_instance2,
        description = "Immediate sale",
        location = "Tehran",
        price = 5000000000,
        payment_method = "lumpsum",
        seller_contact = "https://bama.ir/dealer/5904",
        url = "https://bama.ir/car/detail-7chjai4l-fownix-arrizo6pro-1403",
        type = "free"

    )

@pytest.fixture
def car_instance2():
    return Car.objects.create(
        title = "Toyota Corollaa",
        year = 2020,
        mileage = "20000",
        body_color = "red",
        inside_color = "black",
        body_type ='passenger_car',
        transmission ="automatic" ,
        fuel = "gasoline",
        image = "https://images.app.goo.gl/JVy5hXzcpjAvm72XA"
    )

@pytest.fixture()
def expected_data(ad_instance):

    return  {
            'id': ad_instance.pk,
            'code': ad_instance.code,
            'car': {
                'id': ad_instance.car.pk,
                'title': ad_instance.car.title,
                'year': ad_instance.car.year,
                'mileage': ad_instance.car.mileage,
                'body_color': ad_instance.car.body_color,
                'inside_color': ad_instance.car.inside_color,
                'body_type': ad_instance.car.body_type,
                'transmission': ad_instance.car.transmission,
                'fuel': ad_instance.car.fuel,
                'image': ad_instance.car.image,
            },
            'description': ad_instance.description,
            'location': ad_instance.location,
            'price': ad_instance.price,
            'payment_method': ad_instance.payment_method,
            'seller_contact': ad_instance.seller_contact,
            'url': ad_instance.url,
    }

@pytest.fixture()
def new_ad(ad_instance):

    return  {
            'car': {
                'id': ad_instance.car.pk,
                'title': ad_instance.car.title,
                'year': ad_instance.car.year,
                'mileage': ad_instance.car.mileage,
                'body_color': ad_instance.car.body_color,
                'inside_color': ad_instance.car.inside_color,
                'body_type': ad_instance.car.body_type,
                'transmission': ad_instance.car.transmission,
                'fuel': ad_instance.car.fuel,
                'image': ad_instance.car.image,
            },
            'description': ad_instance.description,
            'location': ad_instance.location,
            'price': ad_instance.price,
            'payment_method': ad_instance.payment_method,
             'type':ad_instance.type,

    }