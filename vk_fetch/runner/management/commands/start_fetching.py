import datetime

from django.utils import timezone
from threading import Thread

import requests
from django.core.management import BaseCommand
from django.db.models import F

from entities.models import VkGroup, VkPost, VkUser, VkUserStatisticTotal, VkUserStatisticDaily, VkUserStatisticHourly

base_url = 'https://api.vk.com/method/{method_name}'
paging = 100

base_request_pairs = (
    ('v', '5.50'),
)
base_iteration_request_pairs = base_request_pairs + (
    ('count', paging),
)


class VkAPI(object):
    WALL_GET = 'wall.get'
    LIKES_GET_LIST = 'likes.getList'
    GROUP_INFO = 'groups.getById'
    USERS_GET = 'users.get'


def _bulk_vk_iterator(method, request_params=None):
    if request_params is None:
        request_params = {}

    offset = 0
    request = dict(base_iteration_request_pairs)
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


def fetch_user(user):
    url = base_url.format(method_name=VkAPI.USERS_GET)
    request = dict(
            base_request_pairs + (
                ('user_ids', user.id),
                ('fields', 'photo_50')
            )
    )
    info = requests \
        .get(url, params=request) \
        .json() \
        .get('response', {})[0]

    user.first_name = info.get('first_name', None)
    user.last_name = info.get('last_name', None)
    user.photo_50 = info.get('photo_50', None)
    user.save()
    return user


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
        fetch_likes(post)
        # fixme: performance
        # fetch_likes_thread = FetchLikes(post)
        # spawned_treads.append(fetch_likes_thread)
        # fetch_likes_thread.start()
        existing_posts.add(post.pk)

    for thread in spawned_treads:
        thread.join()

    VkPost.objects \
        .filter(group=group) \
        .exclude(pk__in=existing_posts).delete()

    print('Processing group <{group_domain}> complete'.format(group_domain=group))


class FetchUser(Thread):
    def __init__(self, user):
        self.user = user
        super(FetchUser, self).__init__()

    def run(self):
        fetch_user(self.user)


def update_users_info():
    threads = []
    for user in VkUser.objects.all():
        fetch_user(user)
        # fixme: performance
        # thread = FetchUser(user)
        # thread.start()
        # threads.append(thread)

    for thread in threads:
        thread.join()


def update_users_statistic():
    now = datetime.datetime.now(timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    current_date = current_hour.replace(hour=0)
    for user in VkUser.objects.all():
        total_statistic, _ = VkUserStatisticTotal.objects.get_or_create(user=user)
        new_likes = user.liked_posts.all().count()
        delta_likes = new_likes - total_statistic.likes

        VkUserStatisticHourly.objects.get_or_create(user=user, timestamp=current_hour)
        VkUserStatisticDaily.objects.get_or_create(user=user, date=current_date)

        VkUserStatisticHourly.objects.filter(user=user, timestamp=current_hour).update(likes=F('likes') + delta_likes)
        VkUserStatisticDaily.objects.filter(user=user, date=current_date).update(likes=F('likes') + delta_likes)

        total_statistic.likes = new_likes
        total_statistic.save()


def process_all():
    for group in VkGroup.objects.all():
        process_group(group)
    update_users_statistic()
    # update_users_info()


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "My test command"

    # A command must define handle()
    def handle(self, *args, **options):
        process_all()
