import os
import sys
import pytest
import asyncio

from unittest.mock import patch, AsyncMock, MagicMock
from aiohttp.client import ClientSession

from crawler_test_data import test_ad_data, cars_instance , ads_instance
from ads.models  import Car,Ad
from crawler import crawler,run_crawler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test__fetch_pages_success(mock_get):
        mock_response = AsyncMock()
        mock_response.json.return_value = test_ad_data
        mock_get.return_value.__aenter__.return_value = mock_response
        fetcher = crawler('https://bama.ir/cad/api/search')
        semaphore = asyncio.Semaphore(10)
        async with ClientSession() as session:
            cars, ads = await fetcher.fetch_pages(session,1,semaphore)
        assert len(cars) == 1
        assert cars[0].title == 'Test Car'
        assert ads[0].price == '10000'


def test__extract_info():
    fetcher = crawler('https://bama.ir/cad/api/search')
    for ad in test_ad_data['data']['ads']:
        car_instance, ad_instance = fetcher.extract_info(ad)
    assert isinstance(car_instance, Car)
    assert isinstance(ad_instance, Ad)
    assert car_instance.title == "Test Car"
    assert ad_instance.code == "TEST123"

@pytest.mark.asyncio
@patch('crawler.crawler.fetch_pages', new_callable=AsyncMock)
@patch('crawler.crawler.save_data', new_callable=AsyncMock)
async def test__create_and_run_tasks(mock_save_data, mock_fetch_pages):
    mock_fetch_pages.return_value = (
        [Car(
            title="test", body_color="blue", mileage="20000",
            year=2020, transmission="Automatic", fuel="Gasoline", image="http://imageurl.com"
        )],
        [Ad(
            code="12345", description="Sample description", price="40000", seller_contact="http://example.com",
            url="http://example.com", location="city", type="free"
        )]
    )

    fetcher = crawler('https://bama.ir/cad/api/search')
    await fetcher.create_and_run_tasks(3)
    mock_fetch_pages.assert_called_once()
    assert mock_save_data.called
    all_cars, all_ads = mock_save_data.call_args[0]
    assert len(all_cars) == 1
    assert len(all_ads) == 1
@pytest.mark.asyncio
@patch('crawler.Ad.objects.bulk_create', new_callable=MagicMock)
@patch('crawler.Car.objects.bulk_create', new_callable=MagicMock)
@patch('crawler.Ad.objects.all', new_callable=MagicMock)
async def test__save_data(mock_all_ads, mock_bulk_create_cars, mock_bulk_create_ads):
    # Mock existing ads
    existing_ads = [
        Ad(code='existing_code_1'),
        Ad(code='existing_code_2')
    ]
    mock_all_ads.return_value = existing_ads
    cars = cars_instance
    ads =  ads_instance
    fetcher = crawler('https://bama.ir/cad/api/search')
    await fetcher.save_data(cars, ads)
    mock_bulk_create_cars.assert_called_once_with([cars[0], cars[1]])
    mock_bulk_create_ads.assert_called_once_with([ads[0], ads[1]])

@pytest.mark.asyncio
@patch('crawler.Ad.objects.bulk_create', new_callable=MagicMock)
@patch('crawler.Car.objects.bulk_create', new_callable=MagicMock)
@patch('crawler.Ad.objects.all', new_callable=MagicMock)
async def test__save_data_no_duplicate_save(mock_all_ads, mock_bulk_create_cars, mock_bulk_create_ads):
    existing_ads = [
        Ad(code='new_code_1'),
        Ad(code='new_code_2')
    ]
    mock_all_ads.return_value = existing_ads
    cars = cars_instance
    ads = ads_instance
    fetcher = crawler('https://bama.ir/cad/api/search')
    await fetcher.save_data(cars, ads)
    mock_bulk_create_cars.assert_not_called()
    mock_bulk_create_ads.assert_not_called()


@patch('crawler.asyncio.run')
@patch('crawler.logger')
def test__run_crawler(mock_logger, mock_asyncio_run):
    mock_asyncio_run.return_value = MagicMock()
    run_crawler()
    mock_asyncio_run.assert_called_once()
    assert any("Crawling process started..." in call[0][0] for call in mock_logger.info.call_args_list)
    assert any("run time:" in call[0][0] for call in mock_logger.info.call_args_list)
