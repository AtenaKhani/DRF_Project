from .views import AdListView,AdDetailView,AdCreateView

from django.urls import path
urlpatterns = [
    path('ads/', AdListView.as_view()),
    path('ads/<pk>', AdDetailView.as_view(),name='ad_detail'),
    path('create-ad/', AdCreateView.as_view()),
]
