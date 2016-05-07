from threading import Thread

from entities.models import VkPost, VkUser
from vk_api import likes_for_post


def fetch_likes(post):
    """
    :param post: VkPost
    :return:
    """
    post.likes.clear()
    for user_id in likes_for_post(post.post_id, post.owner_id):
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


class FetchLikes(Thread):
    def __init__(self, post, *args, **kwargs):
        self.post = post
        super(FetchLikes, self).__init__(*args, **kwargs)

    def run(self):
        fetch_likes(self.post)
