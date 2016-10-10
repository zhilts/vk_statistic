from entities.models import VkGroup
from runner.fetching.groups import process_group
from runner.fetching.users import update_users_info
from vk_api import reload_proxies


def process_all():
    reload_proxies()
    for group in VkGroup.objects.filter(active=True):
        process_group(group)
    update_users_info()
