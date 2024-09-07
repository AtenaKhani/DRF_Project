from .views import AdListView,AdDetailView

from django.urls import path
urlpatterns = [
    path('ads/', AdListView.as_view()),
    path('ads/<pk>', AdDetailView.as_view(),name='ad_detail'),
]
