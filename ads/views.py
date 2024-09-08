from cProfile import label
from random import choices

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Car,Ad
from .serializers import AdListSerializer,AdDetailSerializer,AdCreateSerializer
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
class CarFilter(filters.FilterSet):
    class Meta:
        model = Car
        fields = ['image','year', 'transmission', 'body_type','fuel']

class AdFilter(filters.FilterSet):
    car__image = filters.BooleanFilter(field_name='image', method='filter_has_image', label='Has Image')
    car__year = filters.NumberFilter(field_name='car__year')
    car__transmission = filters.ChoiceFilter(field_name='car__transmission',choices=Car.TRANSMISSION_TYPES)
    car__body_type=filters.ChoiceFilter(field_name='car__body_type',choices=Car.BODY_TYPES)
    car__fuel= filters.ChoiceFilter(field_name='car__fuel', choices=Car.FUEL_TYPES)
    type=filters.ChoiceFilter(field_name='type',choices=Ad.AD_TYPES,label='Ad Type')
    price = filters.BooleanFilter(field_name='price', method='filter_has_price', label='Has Price')
    payment_method = filters.ChoiceFilter(field_name='payment_method', choices=Ad.PAYMENT_METHOD,
                                        label='Payment Method')

    def filter_has_image(self, queryset, name, value):
        if value:
            return queryset.exclude(car__image__isnull=True)
        else:
            return queryset.filter(car__image__isnull=True)

    def filter_has_price(self, queryset, name, value):
        if value:
            return queryset.filter(price__gt=0)
        else:
            return queryset.filter(price=0)

    class Meta:
        model = Ad
        fields = ['car__image','car__year','car__transmission','car__body_type','car__fuel','price','payment_method']
#

class AdListView(generics.ListAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AdFilter
    search_fields = ['car__title', 'location']


class AdDetailView(generics.RetrieveAPIView):
    queryset = Ad.objects.all().order_by('id')
    serializer_class = AdDetailSerializer

class AdCreateView(generics.CreateAPIView):
    queryset = Ad.objects.all().order_by('id')
    serializer_class = AdCreateSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "To post an ad, you need to register or log in."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        elif not user.phone_number:
            return Response(
                {"detail": "Please go to your profile and provide your phone number before posting an ad."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            ad = serializer.save()
            return Response({"message": "Car and Ad created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAdListView(generics.ListAPIView):
    serializer_class = AdListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Ad.objects.filter(user=user)

class UserAdDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AdCreateSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Ad.objects.filter(user=user)