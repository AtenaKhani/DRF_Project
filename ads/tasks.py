import logging

from celery import shared_task
from .crawler import run_crawler

logger = logging.getLogger('ads')
@shared_task
def update_car_data():
    logger.info("Starting car data update task")
    try:
        run_crawler()
        logger.info("Car data updated successfully")
    except Exception as e:
        logger.error(f"Error while updating car data: {e}")

