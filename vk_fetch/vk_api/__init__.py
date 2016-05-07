import requests

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


def get_user_info(user_id):
    url = base_url.format(method_name=VkAPI.USERS_GET)
    request = dict(
            base_request_pairs + (
                ('user_ids', user_id),
                ('fields', 'photo_50')
            )
    )
    info = requests \
        .get(url, params=request) \
        .json() \
        .get('response', {})[0]
    return info


def get_group_info(group_id):
    url = base_url.format(method_name=VkAPI.GROUP_INFO)
    info = requests \
        .get(url, params=dict(group_id=group_id)) \
        .json() \
        .get('response', {})[0]
    return info


def posts_for_group(group_domain):
    return _vk_iterator(
            VkAPI.WALL_GET,
            dict(
                    domain=group_domain,
                    filter='all'
            )
    )


def likes_for_post(post_id, owner_id):
    return _vk_iterator(
            VkAPI.LIKES_GET_LIST,
            dict(
                    type='post',
                    item_id=post_id,
                    owner_id=owner_id
            )
    )