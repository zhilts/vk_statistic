from entities.models import VkRepost, VkUser
from vk_api import reposts_for_post


def fetch_reposts(post):
    """
    :param post: VkPost
    :return:
    """
    VkRepost.objects.filter(post=post).delete()

    if post.reposts_count == 0:
        return
    for repost_data in reposts_for_post(post.post_id, post.owner_id):
        from_id = repost_data.get('from_id', -1)
        if from_id < 0:
            print('from_id = {from_id}'.format(from_id))
            continue
        user, _ = VkUser.objects.get_or_create(id=from_id)
        VkRepost.objects.create(
                vk_id=repost_data.get('id'),
                user=user,
                post=post,
                likes=repost_data.get('likes', {}).get('count', 0),
                reposts=repost_data.get('reposts', {}).get('count', 0)
        )
