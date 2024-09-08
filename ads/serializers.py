from datetime import datetime
import random
import string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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


class AdCreateSerializer(serializers.ModelSerializer):
    car=CarSerializer()
    class Meta :
        model = Ad
        fields = ['car','description','location','price','payment_method','type']
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
    def validate_type(self,value):
        if value == 'premium':
            user = self.context['request'].user
            if user.wallet_balance < 50000:
                raise  serializers.ValidationError("Your wallet balance is less than 50000 Tomans, you cannot register a premium ad")
        return value

    def generate_ad_code(self):
            prefix = "myad-"
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            date_part = datetime.now().strftime('%Y%m%d')
            return f"{prefix}{date_part}-{random_part}"

    def create(self, validated_data):
            car_data = validated_data.pop('car')
            user = self.context['request'].user
            validated_data['code'] = self.generate_ad_code()
            validated_data['seller_contact'] = user.phone_number
            car = Car.objects.create(**car_data)
            ad = Ad.objects.create(**validated_data, car=car,user=user)
            if ad.type == 'premium':
                user.wallet_balance -= 50000
                user.save()
            ad.url = reverse('ad_detail', kwargs={'pk': ad.pk})
            ad.save()
            return ad

    def update(self, instance, validated_data):
        if instance.type == 'free' and validated_data['type']=='premium':
            user = self.context['request'].user
            user.wallet_balance -= 50000
            user.save()
        if instance.type == 'premium' and validated_data['type']=='free':
            raise serializers.ValidationError("You cannot change the premium ad to free")
        car_data = validated_data.pop('car', None)
        if car_data:
            for attr, value in car_data.items():
                setattr(instance.car, attr, value)
            instance.car.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
