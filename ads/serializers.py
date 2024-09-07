from datetime import datetime
import random
import string
from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Car,Ad
from datetime import datetime
import jdatetime
class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

    def validate_year(self, value):
        current_year_miladi = datetime.now().year
        current_year_shamsi = jdatetime.datetime.now().year
        if 1350 <= value <= 1500:
            if value > current_year_shamsi:
                raise serializers.ValidationError("Shamsi year must be between 1350 and the current year.")
        elif 1970 <= value :
            if value > current_year_miladi:
                raise serializers.ValidationError("Miladi year must be between 1970 and the current year.")
        else:
            raise serializers.ValidationError("Year must be either a valid Miladi or Shamsi year.")

        return value




class AdListSerializer(serializers.ModelSerializer):
    car_year = serializers.SerializerMethodField()
    car_title = serializers.SerializerMethodField()
    car_image= serializers.SerializerMethodField()
    def get_car_year(self, obj):
        return obj.car.year if obj.car else None
    def get_car_title(self, obj):
        return obj.car.title if obj.car else None
    def get_car_image(self, obj):
        return obj.car.image if obj.car else None
    class Meta:
        model = Ad
        fields = ['id','car_title','car_year','location','price','payment_method','car_image']


class AdDetailSerializer(serializers.ModelSerializer):
    car=CarSerializer()
    class Meta:
        model = Ad
        fields=['id','code','car','description','location','price','payment_method','seller_contact','url','created_date','modified_date']
