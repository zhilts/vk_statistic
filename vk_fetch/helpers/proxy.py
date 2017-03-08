import logging
from time import time

import re
import requests
from celery import group

from helpers.redis import RedisStorage, get_redis
from vk_fetch.celery import app

import pickle

logger = logging.getLogger(__name__)


class ProxyStorage(object):
    _instance = None
    KEY = 'proxies'

    def __init__(self):
        self.redis = get_redis(RedisStorage.PROXY)

    def set(self, proxy_list):
        return self.redis.set(self.KEY, pickle.dumps(proxy_list))

    def get(self):
        saved_proxies = self.redis.get(self.KEY)
        if saved_proxies is None:
            return []
        return pickle.loads(saved_proxies)


class ProxyManager(object):
    __instance = None
    __timeout = 60 * 10

    def __init__(self):
        self._proxy_storage = ProxyStorage()
        self._current = -1
        self._cached_list = None
        self._cache_updated = 0

    def _get_cached_list(self):
        logger.debug(self._cached_list, self._cache_updated + ProxyManager.__timeout)
        if (self._cached_list is None) \
                or ((self._cache_updated + ProxyManager.__timeout) < time()):
            self._cached_list = self._proxy_storage.get()
            self._cache_updated = time()
            self._current = -1
        return self._cached_list

    def update(self, proxy_list):
        self._proxy_storage.set(proxy_list)

    def get(self):
        proxy_list = self._get_cached_list()
        if self._current == -1 or len(proxy_list) == 0:
            return None
        self._current %= len(proxy_list)
        return proxy_list[self._current]

    def next(self):
        self._current += 1

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = ProxyManager()
        return cls.__instance


@app.task(trail=True)
def test_proxy(proxy):
    logger.debug('testing proxy {proxy}'.format(proxy=proxy))
    url = proxy['host']
    start = time()
    try:
        res = requests.get('https://api.vk.com/method/apps.get?app_id=5539206', proxies={'https': url}, timeout=5)
        timing = time() - start
        logger.debug('test proxy {proxy} success with status={status_code} and timing={timing}'.format(proxy=url,
                                                                                                       status_code=res.status_code,
                                                                                                       timing=timing))
        proxy['timing'] = timing
        if res.status_code == 200:
            return proxy
    except Exception as ex:
        logger.debug('test proxy {proxy} failed with {ex}'.format(proxy=url, ex=ex))


def proxy_list_from_html(html):
    proxies_table = re.search('<tbody>(.*)<\/tbody>', html, re.S).group(1)
    rows = re.split('\n', proxies_table)

    def get_proxy(string):
        try:
            host, port, _, ssl = re.search(
                '<td>(\d+\.\d+\.\d+\.\d+)<\/td><td>(\d+)(.+<td>){5}(\w{2,3})<\/td>.+<\/td>', string).groups()
            if ssl != 'yes':
                return None
            return dict(host=host, port=port)
        except:
            return None

    proxies = filter(lambda x: x is not None, map(get_proxy, rows))
    return list(proxies)


def update_proxies():
    logger.debug('started proxy update')
    proxies_table_page = requests.get('https://free-proxy-list.net/').text

    https_proxies = proxy_list_from_html(proxies_table_page)

    job = group([test_proxy.si(proxy) for proxy in https_proxies])

    print('staaaaart')
    test_proxies = job().get()
    print('finish')

    filtered_proxies = filter(lambda x: x is not None, test_proxies)
    sorted_proxies = sorted(filtered_proxies, key=lambda x: x['timing'])
    proxy_urls = map(lambda x: x['host'], sorted_proxies)

    proxy_list = list(proxy_urls)
    ProxyManager.instance().update(proxy_list)
    logger.info('proxy list updated = {proxy_list}'.format(proxy_list=proxy_list))
