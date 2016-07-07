from __future__ import absolute_import

from logging.config import dictConfig

from celery import chain, group, shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from entities.models import VkGroup
from runner.fetching import process_group, process_all
from vk_fetch.celery import app

logger = get_task_logger(__name__)
print(__name__)

dictConfig(settings.LOGGING)


@shared_task
def fetch_all():
    process_all()


@app.task(trail=True)
def fetch_all__draft():
    logger.debug('started')
    job = chain(update_groups.si(), update_users.si())
    result = job().get()
    logger.debug('ended. res={res}'.format(res=result))


@app.task(trail=True)
def update_groups():
    logger.debug('started')
    job = group([update_group.si(group_id) for group_id in
                 VkGroup.objects.filter(active=True).values_list('pk', flat=True)])

    logger.debug('ended')
    return job.apply_async()


@app.task(trail=True)
def update_group(group_id):
    logger.debug('started with group_id={group_id}'.format(group_id=group_id))
    vk_group = VkGroup.objects.get(pk=group_id)
    process_group(vk_group)
    logger.debug('finished with group_id={group_id}'.format(group_id=group_id))


@app.task(trail=True)
def update_users():
    args = ()
    logger.debug('started with args={args}'.format(args=args))
    logger.debug('finished with args={args}'.format(args=args))
