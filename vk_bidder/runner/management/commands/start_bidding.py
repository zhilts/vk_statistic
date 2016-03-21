import requests
from django.core.management import BaseCommand

from entities.models import VkGroup, VkPost


base_url = 'https://api.vk.com/method/{method_name}'
paging = 100


class VkAPI(object):
    WALL_GET = 'wall.get'


def _bulk_group_iterator(group_domain):
    offset = 0
    request_params = dict(
            domain=group_domain,
            count=paging,
            filter='all',
            v='5.50'
    )
    url = base_url.format(method_name=VkAPI.WALL_GET)
    count = None
    while True:
        request_params['offset'] = offset
        response = requests \
            .get(url, params=request_params) \
            .json() \
            .get('response', {})

        items = response.get('items')

        offset += paging
        count = count or response.get('count', 0)
        yield items

        if offset >= count:
            return


def _group_iterator(group_domain):
    for post_page in _bulk_group_iterator(group_domain):
        for post in post_page:
            yield post


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


def process_group(group):
    print('Starting processing group <{group_domain}>'.format(group_domain=group))
    existing_posts = set()
    for post_data in _group_iterator(group.domain):
        post = process_post(post_data, group)
        existing_posts.add(post.pk)

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
