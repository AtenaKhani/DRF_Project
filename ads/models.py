from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager

user_model = get_user_model()
# Create your models here.
class Car(models.Model):
    TRANSMISSION_TYPES = [
        ('automatic', 'اتوماتیک'),
        ('manual', 'دنده ای'),
    ]

    FUEL_TYPES = [
        ('gasoline', 'بنزینی'),
        ('cng_gasoline', 'دوگانه سوز'),
        ('hybrid', 'هیبریدی'),
        ('diesel', 'دیزلی'),
        ('electric', 'برقی')
    ]

    BODY_TYPES = [
        ('passenger_car', 'سدان'),
        ('crossover', 'کراس اور'),
        ('suv', 'شاسی بلند‌'),
        ('coupe', 'كوپه'),
        ('hatchback', 'هاچپک'),
        ('convertible', 'کروک'),
        ('pickup', 'وانت'),
        ('van', 'ون'),
    ]

    title = models.CharField(max_length=100)
    year = models.IntegerField()
    mileage = models.CharField(max_length=50)
    body_color = models.CharField(max_length=50)
    inside_color = models.CharField(max_length=50)
    body_type= models.CharField(max_length=20,choices=BODY_TYPES,null=True)
    transmission = models.CharField(max_length=20,choices=TRANSMISSION_TYPES)
    fuel = models.CharField(max_length=20,choices=FUEL_TYPES)
    image = models.URLField(max_length=500,null=True)
    objects = Manager()
    def __str__(self):
        return f"{self.title}_({self.year})"

    class Meta:
        db_table = 'car'
class Ad(models.Model):
    PAYMENT_METHOD = [
        ('lumpsum', 'نقدی'),
        ('negotiable', 'توافقی'),
        ('installment', 'اقساطی')

    ]
    AD_TYPES = [
        ('free','رایگان'),
        ('premium','ویژه')
    ]
    code = models.CharField(max_length=50, blank=False, null=False)
    user = models.ForeignKey(user_model, on_delete=models.CASCADE, related_name='user',null=True)
    car = models.OneToOneField(Car, on_delete=models.CASCADE, related_name='car')
    description = models.TextField(max_length=500,null=True)
    location = models.CharField(max_length=100)
    price = models.BigIntegerField()
    payment_method = models.CharField(max_length=20,choices=PAYMENT_METHOD)
    seller_contact=models.CharField(max_length=100,null=True)
    url = models.URLField(max_length=200)
    type=models.CharField(max_length=20,choices=AD_TYPES)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    objects = Manager()
    def __str__(self):
        return self.code

    class Meta:
        db_table = 'ad'
