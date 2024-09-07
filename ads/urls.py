from .views import AdListView, AdDetailView, AdCreateView, UserAdListView, UserAdDetailView

from django.urls import path
urlpatterns = [
    path('ads/', AdListView.as_view()),
    path('ads/<pk>', AdDetailView.as_view(),name='ad_detail'),
    path('create-ad/', AdCreateView.as_view()),
    path('my_ads/',UserAdListView.as_view()),
    path('my_ads/<pk>',UserAdDetailView.as_view())
]
