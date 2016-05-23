from entities.models import VkGroup
from runner.fetching.groups import update_group_info, process_group
from runner.fetching.users import update_users_info, update_users_statistic


def process_all():
    for group in VkGroup.objects.all():
        process_group(group)
        update_users_statistic(group)
    update_users_info()
