from django.db import models

from entities.models import VkUser, VkGroup


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


class VkUserStatisticTotal(VkUserStatisticBase):
    total_score = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_statistic_total'
