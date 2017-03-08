import logging

import requests
from django.core.paginator import Paginator

from helpers.datetime import from_unix_time
from helpers.proxy import ProxyManager

try:
    import httplib
except ImportError:
    import http.client as httplib
httplib.HTTPConnection.debuglevel = 0

base_url = 'https://api.vk.com/method/{method_name}'
paging = 100

base_request_pairs = (
    ('v', '5.50'),
)
base_iteration_request_pairs = base_request_pairs + (
    ('count', paging),
)

logger = logging.getLogger(__name__)

proxy_manager = ProxyManager.instance()


class VkApiError(Exception):
    pass


def default_headers(kwargs):
    headers = {'Accept-Language': 'ru'}
    headers.update(kwargs.get('headers', {}))

    kwargs['headers'] = headers
    kwargs['timeout'] = 10


def default_kwargs(kwargs):
    default_headers(kwargs)


def set_proxy(kwargs, new_proxy):
    if new_proxy is None:
        kwargs.pop('proxies', None)
    else:
        kwargs['proxies'] = {'https': new_proxy}


def update_proxy(kwargs):
    next_proxy = proxy_manager.get()
    set_proxy(kwargs, next_proxy)


def safe_get(*args, **kwargs):
    count = 0
    exception = None

    default_kwargs(kwargs)

    while count < 10:
        try:
            update_proxy(kwargs)
            logger.debug('request with {args} {kwargs} starting'.format(args=args, kwargs=kwargs))
            res = requests.post(*args, **kwargs)
            if res.status_code < 200 or res.status_code >= 400 or res.json().get('error', None) is not None:
                msg = 'response.post() error args={args}, kwargs={kwargs}, res={res}, status={status}' \
                    .format(args=args, kwargs=kwargs, res=res, status=res.status_code)
                raise VkApiError(msg)
            return res
        except Exception as ex:
            logger.debug('request with {args} {kwargs} failed with {ex}'.format(args=args, kwargs=kwargs, ex=ex))
            proxy_manager.next()
            count += 1
            exception = ex

    raise exception


class VkAPI(object):
    WALL_GET = 'wall.get'
    LIKES_GET_LIST = 'likes.getList'
    GROUP_INFO = 'groups.getById'
    USERS_GET = 'users.get'
    REPOSTS_GET_LIST = 'wall.getReposts'


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
        full_response = safe_get(url, data=request) \
            .json()

        response = full_response.get('response', {})
        items = response.get('items')

        offset += paging
        count = count or response.get('count', 0)
        if items is None:
            raise Exception
        yield items

        if offset >= count:
            return


def _vk_iterator(method, parameters):
    for page in _bulk_vk_iterator(method, parameters):
        for item in page:
            yield item


def get_users_info(user_id):
    url = base_url.format(method_name=VkAPI.USERS_GET)
    request = dict(
        base_request_pairs + (
            ('user_ids', user_id),
            ('fields', 'photo_50')
        )
    )
    res = safe_get(url, data=request)
    try:
        info = res \
            .json() \
            .get('response', {})
        return info
    except:
        raise Exception(res)


def get_group_info(group_id):
    url = base_url.format(method_name=VkAPI.GROUP_INFO)
    info = safe_get(url, data=dict(group_id=group_id)) \
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


def posts_for_group_in_period(group_domain, start_date):
    for post in posts_for_group(group_domain):
        post_timestamp = from_unix_time(post.get('date', 0))
        if post_timestamp >= start_date:
            yield post
        else:
            logger.debug('skipping {post_id}'.format(post_id=post.get('id', None)))
            break


def likes_for_post(post_id, owner_id):
    return _vk_iterator(
        VkAPI.LIKES_GET_LIST,
        dict(
            type='post',
            item_id=post_id,
            owner_id=owner_id
        )
    )


def paged_process(enum, process_page=lambda _: None, page_size=300):
    paginator = Paginator(enum, page_size)
    for i in paginator.page_range:
        page = paginator.page(i)
        process_page(page.object_list)


# reposts_for_post

def reposts_for_post(post_id, owner_id):
    return _vk_iterator(
        VkAPI.REPOSTS_GET_LIST,
        dict(
            post_id=post_id,
            owner_id=owner_id
        )
    )
