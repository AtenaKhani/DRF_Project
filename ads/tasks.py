from celery import shared_task
from .crawler import run_crawler
@shared_task
def update_car_data():
    print("Updating car data")
    run_crawler()
