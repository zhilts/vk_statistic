import logging
import multiprocessing

import gevent

from entities.models import VkPost
from runner.fetching.likes import fetch_likes
from runner.fetching.posts import update_post
from runner.fetching.reposts import fetch_reposts
from runner.fetching.statistic import update_users_statistic
from vk_api import get_group_info, posts_for_group


def update_group_info(group):
    group_info = get_group_info(group.domain)
    group.vk_id = group_info.get('gid', None)
    group.save()
    return group


def worker(queue, res):
    while True:
        post_data, group = queue.get()
        try:
            post = update_post(post_data, group)
            fetch_likes(post)
            fetch_reposts(post)
            res.append(post.pk)
        finally:
            queue.task_done()


def get_queue():
    res = []
    queue = gevent.queue.JoinableQueue()
    for i in range(multiprocessing.cpu_count() * 2 + 1):
        gevent.spawn(worker, queue, res)

    return queue, res


def fetch_all(group):
    queue, post_ids = get_queue()
    for post_data in posts_for_group(group.domain):
        queue.put((post_data, group))

    queue.join()
    VkPost.objects \
        .filter(group=group) \
        .exclude(pk__in=post_ids).delete()


logger = logging.getLogger(__name__)


def process_group(group):
    logger.info('Starting processing group <{group_domain}>'.format(group_domain=group))
    group = update_group_info(group)
    fetch_all(group)
    update_users_statistic(group)
    logger.info('Processing group <{group_domain}> complete'.format(group_domain=group))
