from django.db import connection
from django.db.models import F, Sum

from entities.models import VkUserStatisticTotal, VkUser, VkUserStatisticHourly, VkUserStatisticWeekly, \
    VkUserStatisticDaily
from entities.models.RunPeriod import RunPeriod
from entities.models.Settings import SettingsKey
from entities.models.VkInvitation import VkInvitation
from entities.models.VkUserStatistic import VkUserStatisticPeriod
from helpers.datetime import get_now, start_of_current_period, start_of_an_hour, start_of_day, start_of_week
from helpers.settings import rate_settings


def update_users_statistic(group):
    now = get_now()
    current_hour = start_of_an_hour(now)
    current_date = start_of_day(now)
    current_week = start_of_week(now)
    current_run_start = start_of_current_period(now)
    current_run_period, _ = RunPeriod.objects.get_or_create(timestamp=current_run_start)

    def get_sum(s, column):
        return s.aggregate(sum=Sum(column)).get('sum') or 0

    for user in VkUser.objects.all():
        total_statistic, _ = VkUserStatisticTotal.objects.get_or_create(user=user, group=group)

        new_likes = user.liked_posts.filter(group=group).count()
        new_reposts = user.vkrepost_set.count()
        new_likes_for_reposts = get_sum(user.vkrepost_set, 'likes')
        new_reposts_for_reposts = get_sum(user.vkrepost_set, 'reposts')
        new_invites = VkInvitation.objects.filter(group=group, invited_by=user).count()

        delta_likes = new_likes - total_statistic.likes
        delta_reposts = new_reposts - total_statistic.reposts
        delta_likes_for_reposts = new_likes_for_reposts - total_statistic.likes_for_reposts
        delta_reposts_for_reposts = new_reposts_for_reposts - total_statistic.reposts_for_reposts
        delta_invites = new_invites - total_statistic.invites

        VkUserStatisticHourly.objects.get_or_create(user=user, group=group, timestamp=current_hour)
        VkUserStatisticDaily.objects.get_or_create(user=user, group=group, date=current_date)
        VkUserStatisticWeekly.objects.get_or_create(user=user, group=group, week=current_week)
        VkUserStatisticPeriod.objects.get_or_create(user=user, group=group, period=current_run_period)

        update = dict(
            likes=F('likes') + delta_likes,
            reposts=F('reposts') + delta_reposts,
            likes_for_reposts=F('likes_for_reposts') + delta_likes_for_reposts,
            reposts_for_reposts=F('reposts_for_reposts') + delta_reposts_for_reposts,
            invites=F('invites') + delta_invites
        )
        VkUserStatisticHourly.objects.filter(user=user, group=group, timestamp=current_hour).update(**update)
        VkUserStatisticDaily.objects.filter(user=user, group=group, date=current_date).update(**update)
        VkUserStatisticWeekly.objects.filter(user=user, group=group, week=current_week).update(**update)
        VkUserStatisticPeriod.objects.filter(user=user, group=group, period=current_run_period).update(**update)
        VkUserStatisticTotal.objects.filter(user=user, group=group).update(**update)

    update_total_score(group, current_run_period)
    update_rating(group.pk, current_run_period)


def update_total_score_base(group, query, rates):
    query \
        .filter(group=group) \
        .update(total_score=
                F('likes') * rates[SettingsKey.RATE_LIKES]
                + F('reposts') * rates[SettingsKey.RATE_REPOSTS]
                + F('likes_for_reposts') * rates[SettingsKey.RATE_LIKES_FOR_REPOSTS]
                + F('reposts_for_reposts') * rates[SettingsKey.RATE_REPOSTS_FOR_REPOSTS]
                + F('invites') * rates[SettingsKey.RATE_INVITES]
                )


def update_total_score(group, period):
    rates = rate_settings()
    update_total_score_base(group, VkUserStatisticTotal.objects, rates)
    update_total_score_base(group, VkUserStatisticPeriod.objects.filter(period=period), rates)


def update_rating_total(group_id, table_name):
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE {table} t1
        SET {rating_column} = 1 + (SELECT Count(*)
                      FROM {table} t2
                      WHERE t1.{total_score_column} < t2.{total_score_column} AND t2.{group_id_column} = {group_id})
        WHERE {group_id_column} = {group_id};
    """.format(
        group_id=group_id,
        table=table_name,
        total_score_column='total_score',
        rating_column='rating',
        group_id_column='group_id'
    ))


def update_rating_period(group_id, table_name, period_id):
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE {table} t1
        SET {rating_column} = 1 + (SELECT Count(*)
                      FROM {table} t2
                      WHERE t1.{total_score_column} < t2.{total_score_column}
                        AND t2.{group_id_column} = {group_id}
                        AND t2.{period_id_column} = {period_id}
                      )
        WHERE {group_id_column} = {group_id} AND {period_id_column} = {period_id};
    """.format(
        group_id=group_id,
        table=table_name,
        total_score_column='total_score',
        rating_column='rating',
        group_id_column='group_id',
        period_id_column='period_id',
        period_id=period_id,
    ))


def update_rating(group_id, period):
    update_rating_total(group_id, VkUserStatisticTotal._meta.db_table)
    update_rating_period(group_id, VkUserStatisticPeriod._meta.db_table, period.pk)
