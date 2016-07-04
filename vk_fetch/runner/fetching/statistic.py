import datetime

from django.db.models import F
from django.utils import timezone

from entities.models import VkUserStatisticTotal, VkUser, VkUserStatisticHourly, VkUserStatisticWeekly, \
    VkUserStatisticDaily


def update_users_statistic(group):
    now = datetime.datetime.now(datetime.timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    current_date = current_hour.replace(hour=0)
    current_week = current_date - datetime.timedelta(days=current_date.weekday())

    for user in VkUser.objects.all():
        total_statistic, _ = VkUserStatisticTotal.objects.get_or_create(user=user, group=group)
        new_likes = user.liked_posts.filter(group=group).count()
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
        total_statistic.total_score = new_likes
        total_statistic.save()
