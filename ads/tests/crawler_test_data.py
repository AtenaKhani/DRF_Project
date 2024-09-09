import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ads.models  import Car,Ad
test_ad_data = {
    'status': True,
    'data': {
        'ads': [
            {
                'detail': {
                    'title': 'Test Car',
                    'year': 2020,
                    'mileage': '10000',
                    'body_color': 'Red',
                    'inside_color': 'Black',
                    'body_type_fa': 'سدان',
                    'transmission': 'اتوماتیک',
                    'fuel': 'بنزینی',
                    'image': 'http://example.com/image.jpg',
                    'url': '/car/test',
                    'code': 'TEST123',
                    'description': 'Test description',
                    'location': 'Test location'
                },
                'price': {
                    'price': '10000',
                    'type': 'Cash'
                },
                'dealer': {
                    'link': '/dealer/test'
                }
            }
        ]
    }
}



cars_instance = [
        Car(title="Car 1", body_color="red", mileage="10000", year=2022, transmission="automatic", fuel="petrol",
            image="http://example.com/image1.jpg"),
        Car(title="Car 2", body_color="blue", mileage="20000", year=2021, transmission="manual", fuel="diesel",
            image="http://example.com/image2.jpg")
    ]
ads_instance = [
        Ad(code='new_code_1', user=None, car=cars_instance[0], description='description1', location='location1', price='50000',
           payment_method='cash', seller_contact='contact1', url='http://example.com/ad1', type='free'),
        Ad(code='new_code_2', user=None, car=cars_instance[1], description='description2', location='location2', price='60000',
           payment_method='credit', seller_contact='contact2', url='http://example.com/ad2', type='paid')
    ]

