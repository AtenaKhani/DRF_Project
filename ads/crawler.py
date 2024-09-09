import aiohttp
import asyncio
import logging

from time import time
from aiohttp.client import ClientSession
from asgiref.sync import sync_to_async
from ads.models import Car,Ad


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class crawler:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def fetch_pages(self, session: ClientSession, page: int, semaphore: asyncio.Semaphore):
        async with semaphore:
            async with session.get(f'{self.api_url}?pageIndex={page}', headers=self.headers) as response:
                try:
                    data = await response.json()
                    if data.get('status') and 'data' in data and 'ads' in data['data']:
                        cars_list, ads_list = [], []
                        for ad in data['data']['ads']:
                            car, ad_info = self.extract_info(ad)
                            cars_list.append(car)
                            ads_list.append(ad_info)
                        logger.info(f"Successfully fetched data from page {page}.")
                        return cars_list, ads_list

                    else:
                        logger.warning(f"Data not found on page {page}.")

                except aiohttp.ContentTypeError:
                    logger.error(f"Error parsing JSON on page {page}.")

                except aiohttp.ClientResponseError as e:
                    print(f"HTTP request error on page {page}: {e}")
                    # logger.error(f"HTTP request error on page {page}.")

    def extract_info(self, ad):
        def get_display_value(choices, key):
            for k, v in choices:
                if v == key:
                    return k
            return None
        details = ad.get('detail', {})
        price_info = ad.get('price', {})
        dealer = ad.get('dealer', {})
        details = details if details is not None else {}
        price_info = price_info if price_info is not None else {}
        dealer = dealer if dealer is not None else {}
        price = price_info.get('price')
        url = details.get('url')
        link =dealer.get('link')
        if price is not None:
            price = price_info.get('price').replace(",", "")
        if url  is not None:
            url = "https://bama.ir" + url
        if link is not None:
            link= "https://bama.ir" + link
        car_instance=Car(
            title=details.get('title'),
            year=details.get('year'),
            mileage=details.get('mileage'),
            body_color=details.get('body_color'),
            inside_color=details.get('inside_color'),
            body_type=get_display_value(Car.BODY_TYPES,details.get('body_type_fa')),
            transmission=get_display_value(Car.TRANSMISSION_TYPES,details.get('transmission')),
            fuel=get_display_value(Car.FUEL_TYPES,details.get('fuel')),
            image=details.get('image'),

        )
        return car_instance,Ad(
            code=details.get('code'),
            user=None,
            car=car_instance,
            description=details.get('description'),
            location=details.get('location'),
            price=price,
            payment_method=price_info.get('type'),
            seller_contact=link,
            url = url,
            type='free',

        )

    async def create_and_run_tasks(self, pages: int):
        all_cars = []
        all_ads=[]
        semaphore = asyncio.Semaphore(10)
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_pages(session, page, semaphore) for page in range(3, pages + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"An error occurred: {result}")
                    continue

                if isinstance(result, tuple) and len(result) == 2:
                    cars_list, ads_list = result
                    if isinstance(cars_list, list) and isinstance(ads_list, list):
                        all_cars.extend(cars_list)
                        all_ads.extend(ads_list)
        await self.save_data(all_cars,all_ads)
        logger.error(f"{len(all_ads)} ads have been successfully extracted .")

    async def save_data(self,cars, ads):
        ads = [ad for ad in ads]
        cars = [car for car in cars]
        new_ads=[]
        new_cars=[]
        existing_ads = await sync_to_async(lambda: list(Ad.objects.all()))()
        existing_codes = [ad.code for ad in existing_ads]
        index = 0
        for ad in ads:
            if ad.code not in existing_codes:
                new_ads.append(ad)
                new_cars.append(cars[index])
            index+=1
        if new_ads:
            await sync_to_async(Car.objects.bulk_create)(new_cars)
            await sync_to_async(Ad.objects.bulk_create)(new_ads)
            logger.info(f"Saved {len(new_ads)} new ads and {len(new_cars)} new cars to the database.")

def run_crawler():
    fetcher = crawler('https://bama.ir/cad/api/search')
    logger.info("Crawling process started...")
    start = time()
    asyncio.run(fetcher.create_and_run_tasks(10))
    logger.info(f"run time: {time() - start} seconds")
