from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger
from logging.config import dictConfig
from settings.settings import LOGGING

from runner.fetching import process_all


def log_info(msg):
    dictConfig(LOGGING)
    logger = get_task_logger('celery')
    logger.info(msg)


@shared_task
def fetch_all():
    result = process_all()
    log_info('task fetch_all finished with result = {result}'.format(result=str(result)))
