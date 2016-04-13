from threading import Thread

import requests
from django.core.management import BaseCommand

from entities.models import VkGroup, VkPost, VkUser

base_url = 'https://api.vk.com/method/{method_name}'
paging = 100


class VkAPI(object):
    WALL_GET = 'wall.get'
    LIKES_GET_LIST = 'likes.getList'
    GROUP_INFO = 'groups.getById'


def _bulk_vk_iterator(method, request_params=None):
    if request_params is None:
        request_params = {}

    offset = 0
    request = dict(
            count=paging,
            v='5.50'
    )
    request.update(request_params)
    url = base_url.format(method_name=method)
    count = None
    while True:
        request['offset'] = offset
        response = requests \
            .get(url, params=request) \
            .json() \
            .get('response', {})

        items = response.get('items')

        offset += paging
        count = count or response.get('count', 0)
        yield items

        if offset >= count:
            return


def _vk_iterator(method, parameters):
    for page in _bulk_vk_iterator(method, parameters):
        for item in page:
            yield item


def _group_iterator(group_domain):
    return _vk_iterator(
            VkAPI.WALL_GET,
            dict(
                    domain=group_domain,
                    filter='all'
            )
    )


def _likes_iterator(post):
    return _vk_iterator(
            VkAPI.LIKES_GET_LIST,
            dict(
                    type='post',
                    item_id=post.post_id,
                    owner_id=post.owner_id
            )
    )


def fetch_likes(post):
    """
    :param post: VkPost
    :return:
    """
    post.likes.clear()
    for user_id in _likes_iterator(post):
        user, _ = VkUser.objects.get_or_create(id=user_id)
        post.likes.add(user)


def process_post(post_data, group):
    post, _ = VkPost.objects.update_or_create(
            post_id=post_data['id'],
            group=group,
            defaults=dict(
                    likes_count=post_data.get('likes', {}).get('count'),
                    reposts_count=post_data.get('reposts', {}).get('count'),
                    text=post_data.get('text', None)
            )
    )
    return post


def update_group_info(group):
    url = base_url.format(method_name=VkAPI.GROUP_INFO)
    response = requests \
        .get(url, params=dict(group_id=group.domain)) \
        .json() \
        .get('response', {})[0]

    group.name = response.get('name', None)
    group.vk_id = response.get('gid', None)
    group.save()
    return group


class FetchLikes(Thread):
    def __init__(self, post, *args, **kwargs):
        self.post = post
        super(FetchLikes, self).__init__(*args, **kwargs)

    def run(self):
        fetch_likes(self.post)


def process_group(group):
    print('Starting processing group <{group_domain}>'.format(group_domain=group))
    group = update_group_info(group)
    existing_posts = set()
    spawned_treads = []
    for post_data in _group_iterator(group.domain):
        post = process_post(post_data, group)
        fetch_likes_thread = FetchLikes(post)
        spawned_treads.append(fetch_likes_thread)
        fetch_likes_thread.start()
        existing_posts.add(post.pk)

    for thread in spawned_treads:
        thread.join()

    VkPost.objects \
        .filter(group=group) \
        .exclude(pk__in=existing_posts).delete()

    print('Processing group <{group_domain}> complete'.format(group_domain=group))


def process_all():
    for group in VkGroup.objects.all():
        process_group(group)


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "My test command"

    # A command must define handle()
    def handle(self, *args, **options):
        process_all()
