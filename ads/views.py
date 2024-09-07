
from rest_framework import generics, status
#
from .models import Car,Ad
from .serializers import AdListSerializer,AdDetailSerializer

class AdListView(generics.ListAPIView):
    queryset = Ad.objects.all().order_by('id')
    serializer_class = AdListSerializer


class AdDetailView(generics.RetrieveAPIView):
    queryset = Ad.objects.all().order_by('id')
    serializer_class = AdDetailSerializer
