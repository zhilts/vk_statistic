import time

from entities.models import VkGroup
from runner.fetching.groups import process_group
from runner.fetching.users import update_users_info


def timed(fn):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = fn(*args, **kwargs)
        end = time.time()
        return (res, end - start)

    return wrapper


@timed
def process_all():
    for group in VkGroup.objects.filter(active=True):
        process_group(group)
    update_users_info()
