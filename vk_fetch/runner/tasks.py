from __future__ import absolute_import

from celery import shared_task

from runner.fetching import process_all


@shared_task
def fetch_all():
    process_all()
