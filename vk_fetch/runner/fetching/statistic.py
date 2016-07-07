import datetime

from django.db import connection
from django.db.models import F, Sum
from django.utils import timezone

from entities.models import VkUserStatisticTotal, VkUser, VkUserStatisticHourly, VkUserStatisticWeekly, \
    VkUserStatisticDaily


def update_users_statistic(group):
    now = datetime.datetime.now(datetime.timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    current_date = current_hour.replace(hour=0)
    current_week = current_date - datetime.timedelta(days=current_date.weekday())

    def get_sum(s, column):
        return s.aggregate(sum=Sum(column)).get('sum') or 0

    for user in VkUser.objects.all():
        total_statistic, _ = VkUserStatisticTotal.objects.get_or_create(user=user, group=group)

        new_likes = user.liked_posts.filter(group=group).count()
        new_reposts = user.vkrepost_set.count()
        new_likes_for_reposts = get_sum(user.vkrepost_set, 'likes')
        new_reposts_for_reposts = get_sum(user.vkrepost_set, 'reposts')

        delta_likes = new_likes - total_statistic.likes
        delta_reposts = new_reposts - total_statistic.reposts
        delta_likes_for_reposts = new_likes_for_reposts - total_statistic.likes_for_reposts
        delta_reposts_for_reposts = new_reposts_for_reposts - total_statistic.reposts_for_reposts

        VkUserStatisticHourly.objects.get_or_create(user=user, group=group, timestamp=current_hour)
        VkUserStatisticDaily.objects.get_or_create(user=user, group=group, date=current_date)
        VkUserStatisticWeekly.objects.get_or_create(user=user, group=group, week=current_week)

        update = dict(
                likes=F('likes') + delta_likes,
                reposts=F('reposts') + delta_reposts,
                likes_for_reposts=F('likes_for_reposts') + delta_likes_for_reposts,
                reposts_for_reposts=F('reposts_for_reposts') + delta_reposts_for_reposts
        )
        VkUserStatisticHourly.objects.filter(user=user, group=group, timestamp=current_hour).update(**update)
        VkUserStatisticDaily.objects.filter(user=user, group=group, date=current_date).update(**update)
        VkUserStatisticWeekly.objects.filter(user=user, group=group, week=current_week).update(**update)
        VkUserStatisticTotal.objects.filter(user=user, group=group).update(**update)

    update_total_score(group)
    update_rating(group.pk)


def update_total_score(group):
    VkUserStatisticTotal.objects \
        .filter(group=group) \
        .update(total_score=F('likes') + F('reposts') + F('likes_for_reposts') + F('reposts_for_reposts'))


def update_rating(group_id):
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE {table} t1
        SET {rating_column} = (SELECT Count(*)
                      FROM {table} t2
                      WHERE t1.{total_score_column} < t2.{total_score_column} AND t2.{group_id_column} = {group_id})
        WHERE {group_id_column} = {group_id};
    """.format(
            group_id=group_id,
            table=VkUserStatisticTotal._meta.db_table,
            total_score_column='total_score',
            rating_column='rating',
            group_id_column='group_id'
            # score_column=VkUserStatisticTotal.total_score
    ))
