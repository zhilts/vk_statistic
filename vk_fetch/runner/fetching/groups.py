import logging

from celery import group

from entities.models import VkPost
from runner.fetching.likes import fetch_likes
from runner.fetching.posts import update_post
from runner.fetching.reposts import fetch_reposts
from runner.fetching.statistic import update_users_statistic
from vk_api import get_group_info, posts_for_group
from vk_fetch.celery import app


def update_group_info(group):
    group_info = get_group_info(group.domain)
    group.vk_id = group_info.get('gid', None)
    group.save()
    return group


@app.task(trail=True)
def process_post_data(post_data, group):
    logger.debug('post {post_id} starting process'.format(post_id=post_data['id']))
    post = update_post(post_data, group)
    fetch_likes(post)
    fetch_reposts(post)
    logger.debug('post {post_id} processed'.format(post_id=post_data['id']))
    return post.pk


def fetch_all(vk_group):
    job = group([process_post_data.si(post_data, vk_group) for post_data in posts_for_group(vk_group.domain)])
    post_ids = job.apply_async().get()

    VkPost.objects \
        .filter(group=vk_group) \
        .exclude(pk__in=post_ids).delete()


logger = logging.getLogger(__name__)


def process_group(group):
    logger.info('Starting processing group <{group_domain}>'.format(group_domain=group))
    group = update_group_info(group)
    fetch_all(group)
    update_users_statistic(group)
    logger.info('Processing group <{group_domain}> complete'.format(group_domain=group))
