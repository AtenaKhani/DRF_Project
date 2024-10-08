from rest_framework.urls import app_name

from .views import AdListView, AdDetailView, AdCreateView, UserAdListView, UserAdDetailView
from django.urls import path
app_name = "ads"
urlpatterns = [
    path('ads/', AdListView.as_view(),name='ad_list'),
    path('ads/<pk>', AdDetailView.as_view(),name='ad_detail'),
    path('create-ad/', AdCreateView.as_view(),name='create_ad'),
    path('my_ads/',UserAdListView.as_view(),name='my_ads'),
    path('my_ads/<pk>',UserAdDetailView.as_view(),name='detail_my_ad')
]
