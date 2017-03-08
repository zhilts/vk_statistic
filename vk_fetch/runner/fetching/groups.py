import logging

from celery import group

from entities.models.RunPeriod import RunPeriod
from runner.fetching.posts import process_post_data
from runner.fetching.statistic import update_users_statistic
from vk_api import get_group_info, posts_for_group_in_period


logger = logging.getLogger(__name__)


def update_group_info(group):
    group_info = get_group_info(group.domain)
    group.vk_id = group_info.get('gid', None)
    group.save()
    return group

def fetch_all(vk_group, period):
    posts = posts_for_group_in_period(vk_group.domain, period.timestamp)
    jobs = [process_post_data.si(post_data, vk_group) for post_data in posts]
    return group(jobs)().get()


def process_group(group, period_id):
    logger.info('Starting processing group <{group_domain}>'.format(group_domain=group))
    group = update_group_info(group)
    period = RunPeriod.objects.get(pk=period_id)
    fetch_all(group, period)
    update_users_statistic(group)
    logger.info('Processing group <{group_domain}> complete'.format(group_domain=group))
