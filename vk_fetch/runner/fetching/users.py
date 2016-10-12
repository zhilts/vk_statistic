from entities.models import VkUser
from vk_api import get_users_info, paged_process


def process_users_page(users_ids):
    query = ','.join(map(str, users_ids))
    for info in get_users_info(query):
        VkUser.objects.update_or_create(
            id=info.get('id'),
            defaults=dict(
                first_name=info.get('first_name', None),
                last_name=info.get('last_name', None),
                photo_50=info.get('photo_50', None)
            )
        )



def update_users_info():
    user_ids_qs = VkUser.objects \
        .values_list('id', flat=True) \
        .order_by('id')
    paged_process(user_ids_qs, process_users_page, page_size=1000)
