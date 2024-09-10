import random
import string
import logging
import jdatetime

from rest_framework import serializers
from rest_framework.reverse import reverse
from datetime import datetime

from .models import Car,Ad

logger = logging.getLogger('ads')


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

    def validate_year(self, value):
        current_year_miladi = datetime.now().year
        current_year_shamsi = jdatetime.datetime.now().year
        if 1350 <= value <= 1500:
            if value > current_year_shamsi:
                logger.error(f'Invalid Shamsi year: {value}. It should not be greater than the current year.')
                raise serializers.ValidationError("Shamsi year must be between 1350 and the current year.")
        elif 1970 <= value :
            if value > current_year_miladi:
                logger.error(f'Invalid Miladi year: {value}. It should not be greater than the current year.')
                raise serializers.ValidationError("Miladi year must be between 1970 and the current year.")
        else:
            logger.error(f'Invalid year: {value}. It must be either a valid Miladi or Shamsi year.')
            raise serializers.ValidationError("Year must be either a valid Miladi or Shamsi year.")
        logger.info(f'Year validated successfully: {value}')
        return value


class AdListSerializer(serializers.ModelSerializer):
    is_premium = serializers.SerializerMethodField()

    def get_is_premium(self, obj):
        return obj.type == 'premium'

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
        fields = ['id','car_title','car_year','location','price','payment_method','car_image','is_premium']


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
            logger.error(f'Invalid price : {value}.Price cannot be negative.')
            raise serializers.ValidationError("Price cannot be negative.")
        return value
    def validate_type(self,value):
        user = self.context['request'].user
        if value == 'premium':
            if user.wallet_balance < 50000:
                logger.error(
                    f'User {user.email} attempted to register a premium ad with insufficient wallet balance.')
                raise  serializers.ValidationError("Your wallet balance is less than 50000 Tomans, you cannot register a premium ad")
        logger.info(f'User {user.email} is allowed to register a premium ad.')
        return value

    def generate_ad_code(self):
            prefix = "myad-"
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            date_part = datetime.now().strftime('%Y%m%d')
            ad_code = f"{prefix}{date_part}-{random_part}"
            logger.info(f'Generated ad code: {ad_code}')
            return ad_code

    def create(self, validated_data):
            car_data = validated_data.pop('car')
            user = self.context['request'].user
            validated_data['code'] = self.generate_ad_code()
            validated_data['seller_contact'] = user.phone_number
            logger.info(f'Creating ad with validated data: {validated_data}')
            car = Car.objects.create(**car_data)
            logger.info(f'Car created with ID: {car.id}')
            ad = Ad.objects.create(**validated_data, car=car,user=user)
            logger.info(f'Ad created with ID: {ad.id}, Code: {ad.code}')
            if ad.type == 'premium':
                user.wallet_balance -= 50000
                user.save()
                logger.info(f'Premium ad created. deducted 50000 Tomans from user ID: {user.id}')

            ad.url = reverse('ads:ad_detail', kwargs={'pk': ad.pk})
            ad.save()
            return ad

    def update(self, instance, validated_data):
        if instance.type == 'free' and validated_data['type']=='premium':
            user = self.context['request'].user
            user.wallet_balance -= 50000
            user.save()
            logger.info(
                f'User ID: {user.id} upgraded ad ID: {instance.id} to premium. deducted 50000 Tomans from wallet.')
        if instance.type == 'premium' and validated_data['type']=='free':
            logger.error(
                f'User ID: {self.context["request"].user.id} attempted to change ad ID: {instance.id} '
                f'from premium to free. This operation is not allowed.')
            raise serializers.ValidationError("You cannot change the premium ad to free")
        car_data = validated_data.pop('car', None)
        if car_data:
            for attr, value in car_data.items():
                setattr(instance.car, attr, value)
            instance.car.save()
            logger.info(f'Updated car details for ad ID: {instance.id}.')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        logger.info(f'Updated ad ID: {instance.id}.')
        return instance
