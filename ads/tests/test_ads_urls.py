import pytest
from rest_framework import status
from django.urls import reverse, resolve
from ads.views import AdListView,AdDetailView,UserAdListView,UserAdDetailView

class TestUrl:
    def test__ad_list_url_resolves_to_ad_list_view(self):
            url = reverse('ads:ad_list')
            resolver_match = resolve(url)
            assert resolver_match.view_name == 'ads:ad_list'
            assert resolver_match.func.__name__ == AdListView.as_view().__name__


    def test__ad_detail_url_resolves_to_ad_detail_view(self):
            url = reverse('ads:ad_detail', args=[1])
            resolver_match = resolve(url)
            assert resolver_match.view_name == 'ads:ad_detail'
            assert resolver_match.func.__name__ == AdDetailView.as_view().__name__

    def test__my_ads_url_resolves_to_my_ads_view(self):
            url = reverse('ads:my_ads')
            resolver_match = resolve(url)
            assert resolver_match.view_name == 'ads:my_ads'
            assert resolver_match.func.__name__ == UserAdListView.as_view().__name__

    def test__detail_my_ad_url_resolves_to_detail_my_ad_view(self):
        url = reverse('ads:detail_my_ad',args=[1])
        resolver_match = resolve(url)
        assert resolver_match.view_name == 'ads:detail_my_ad'
        assert resolver_match.func.__name__ == UserAdDetailView.as_view().__name__