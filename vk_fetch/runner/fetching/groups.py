from entities.models import VkPost
from runner.fetching.likes import fetch_likes
from runner.fetching.posts import update_post
from runner.fetching.reposts import fetch_reposts
from runner.fetching.statistic import update_users_statistic
from vk_api import get_group_info, posts_for_group


def update_group_info(group):
    group_info = get_group_info(group.domain)
    group.name = group_info.get('name', None)
    group.vk_id = group_info.get('gid', None)
    group.save()
    return group


def process_group(group):
    print('Starting processing group <{group_domain}>'.format(group_domain=group))
    group = update_group_info(group)
    existing_posts = set()
    spawned_treads = []
    for post_data in posts_for_group(group.domain):
        post = update_post(post_data, group)
        fetch_likes(post)
        fetch_reposts(post)
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

    update_users_statistic(group)

    print('Processing group <{group_domain}> complete'.format(group_domain=group))
