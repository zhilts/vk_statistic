from __future__ import absolute_import

from celery import shared_task

from runner.fetching import process_all


@shared_task
def fetch_all():
    result = process_all()
    print('task fetch_all finished with result = {result}'.format(result=str(result)))
