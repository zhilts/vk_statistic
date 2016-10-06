from django.db import models

from entities.models import VkUser, VkGroup
from entities.models.RunPeriod import RunPeriod


class VkUserStatisticBase(models.Model):
    group = models.ForeignKey(VkGroup, null=False)
    user = models.ForeignKey(VkUser, null=False)
    likes = models.IntegerField(default=0)
    reposts = models.IntegerField(default=0)
    likes_for_reposts = models.IntegerField(default=0)
    reposts_for_reposts = models.IntegerField(default=0)
    invites = models.IntegerField(default=0)

    class Meta:
        abstract = True


class VkUserStatisticHourly(VkUserStatisticBase):
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'user_statistic_hourly'


class VkUserStatisticDaily(VkUserStatisticBase):
    date = models.DateField()

    class Meta:
        db_table = 'user_statistic_daily'


class VkUserStatisticWeekly(VkUserStatisticBase):
    week = models.DateField()

    class Meta:
        db_table = 'user_statistic_weekly'


class VkUserStatisticTotalAbstract(VkUserStatisticBase):
    total_score = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)

    class Meta:
        abstract = True


class VkUserStatisticTotal(VkUserStatisticTotalAbstract):
    class Meta:
        db_table = 'user_statistic_total'


class VkUserStatisticPeriod(VkUserStatisticTotalAbstract):
    period = models.ForeignKey(RunPeriod, null=False)

    class Meta:
        db_table = 'user_statistic_period'
