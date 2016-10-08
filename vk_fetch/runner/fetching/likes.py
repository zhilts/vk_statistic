from threading import Thread

from entities.models import VkUser
from vk_api import likes_for_post


def fetch_likes(post):
    """
    :param post: VkPost
    :return:
    """
    post.likes.clear()
    if post.likes_count == 0:
        return
    for user_id in likes_for_post(post.post_id, post.owner_id):
        user, _ = VkUser.objects.get_or_create(id=user_id)
        post.likes.add(user)


class FetchLikes(Thread):
    def __init__(self, post, *args, **kwargs):
        self.post = post
        super(FetchLikes, self).__init__(*args, **kwargs)

    def run(self):
        fetch_likes(self.post)
