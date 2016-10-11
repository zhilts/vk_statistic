import redis

from django.conf import settings

_instances = {}


def new_connection(config_name):
    config = settings.REDIS_STORAGE[config_name]
    return redis.Redis(host=config['HOST'], port=config['PORT'], db=config['DB'])


def get_redis(config_name):
    connection = _instances.get(config_name, None)
    if connection is None:
        connection = new_connection(config_name)
        _instances[config_name] = connection

    return connection


class RedisStorage:
    PROXY = 'proxy'
