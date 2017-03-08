from __future__ import absolute_import

from logging.config import dictConfig

from celery import chain, group
from celery import states
from celery.utils.log import get_task_logger
from django.conf import settings
from djcelery.models import TaskMeta

from entities.models import VkGroup
from entities.models import VkUser
from entities.models.VkInvitation import VkInvitation
from helpers.datetime import current_period
from helpers.proxy import update_proxies
from runner.fetching.groups import process_group
from runner.fetching.users import update_users_info
from vk_fetch.celery import app

logger = get_task_logger(__name__)

dictConfig(settings.LOGGING)


@app.task()
def reload_all_proxies():
    update_proxies()


@app.task(trail=True)
def fetch_all():
    period = current_period()
    job = chain(
        # reload_all_proxies.si(),
        update_groups.si(period.pk),
        # update_all_users.si()
    )()
    return job.get()


@app.task(trail=True)
def update_groups(period_id):
    job = group([update_group.si(group_id, period_id) for group_id in
                 VkGroup.objects.filter(active=True).values_list('pk', flat=True)])()

    return job.get()


@app.task(trail=True)
def update_group(group_id, period_id):
    logger.debug('started with group_id={group_id}'.format(group_id=group_id))
    vk_group = VkGroup.objects.get(pk=group_id)
    process_group(vk_group, period_id)
    logger.debug('finished with group_id={group_id}'.format(group_id=group_id))


@app.task(trail=True)
def update_all_users():
    update_users_info()


@app.task()
def add_invite(group_id, user_id, viewer_id):
    if user_id == viewer_id:
        return
    viewer, _ = VkUser.objects.get_or_create(pk=viewer_id)
    invited_by, _ = VkUser.objects.get_or_create(pk=user_id)
    group = VkGroup.objects.get(vk_id=group_id)
    try:
        VkInvitation.objects.create(group=group, user=viewer, invited_by=invited_by)
    except Exception as ex:
        logger.debug('invitation failed {err}'.format(err=ex))


@app.task()
def update_users(user_ids=None):
    return update_users_info(user_ids)


@app.task()
def clean_success_taskmeta():
    TaskMeta.objects \
        .filter(status=states.SUCCESS) \
        .delete()
