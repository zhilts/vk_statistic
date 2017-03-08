import logging

from entities.models import VkPost
from entities.models import VkUser
from helpers.datetime import from_unix_time
from runner.fetching.likes import fetch_likes
from runner.fetching.reposts import fetch_reposts
from vk_fetch.celery import app

logger = logging.getLogger(__name__)


def update_post(post_data, group):
    from_id = post_data.get('from_id', None)
    date = from_unix_time(post_data.get('date', 0))
    author = VkUser.objects.get_or_create(id=from_id)[0] if from_id > 0 else None
    post, _ = VkPost.objects.update_or_create(
        post_id=post_data['id'],
        group=group,
        from_id=from_id,
        author=author,
        date=date,
        defaults=dict(
            likes_count=post_data.get('likes', {}).get('count'),
            reposts_count=post_data.get('reposts', {}).get('count'),
            text=post_data.get('text', None)
        )
    )
    return post


@app.task(trail=True)
def process_post_data(post_data, group):
    logger.debug('post {post_id} starting process'.format(post_id=post_data['id']))
    post = update_post(post_data, group)
    fetch_likes(post)
    fetch_reposts(post)
    logger.debug('post {post_id} processed'.format(post_id=post_data['id']))
    return post.pk
