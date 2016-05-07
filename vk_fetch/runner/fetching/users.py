import datetime
from threading import Thread

from django.db.models import F
from django.utils import timezone

from entities.models import VkUser, VkUserStatisticTotal, VkUserStatisticHourly, VkUserStatisticDaily, \
    VkUserStatisticWeekly
from vk_api import get_user_info


def fetch_user(user):
    info = get_user_info(user.id)
    user.first_name = info.get('first_name', None)
    user.last_name = info.get('last_name', None)
    user.photo_50 = info.get('photo_50', None)
    user.save()
    return user


class FetchUser(Thread):
    def __init__(self, user):
        self.user = user
        super(FetchUser, self).__init__()

    def run(self):
        fetch_user(self.user)


def update_users_info():
    threads = []
    for user in VkUser.objects.all():
        fetch_user(user)
        # fixme: performance
        # thread = FetchUser(user)
        # thread.start()
        # threads.append(thread)

    for thread in threads:
        thread.join()


def update_users_statistic(group):
    now = datetime.datetime.now(timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    current_date = current_hour.replace(hour=0)
    current_week = current_date - datetime.timedelta(days=current_date.weekday())

    for user in VkUser.objects.all():
        total_statistic, _ = VkUserStatisticTotal.objects.get_or_create(user=user, group=group)
        new_likes = user.liked_posts.all().count()
        delta_likes = new_likes - total_statistic.likes

        VkUserStatisticHourly.objects.get_or_create(user=user, group=group, timestamp=current_hour)
        VkUserStatisticDaily.objects.get_or_create(user=user, group=group, date=current_date)
        VkUserStatisticWeekly.objects.get_or_create(user=user, group=group, week=current_week)

        VkUserStatisticHourly.objects.filter(user=user, group=group, timestamp=current_hour) \
            .update(likes=F('likes') + delta_likes)
        VkUserStatisticDaily.objects.filter(user=user, group=group, date=current_date) \
            .update(likes=F('likes') + delta_likes)
        VkUserStatisticWeekly.objects.filter(user=user, group=group, week=current_week) \
            .update(likes=F('likes') + delta_likes)

        total_statistic.likes = new_likes
        total_statistic.save()
