from __future__ import absolute_import

from celery import shared_task

from runner.fetching import process_all
from runner.fetching.statistic import update_rating as update_group_rating


@shared_task
def fetch_all():
    process_all()


@shared_task
def update_rating(group):
    update_group_rating(group)
