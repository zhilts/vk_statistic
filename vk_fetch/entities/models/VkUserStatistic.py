from django.db import models

from entities.models import VkUser


class VkUserStatisticBase(models.Model):
    user = models.ForeignKey(VkUser)
    likes = models.IntegerField(default=0)

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


class VkUserStatisticTotal(VkUserStatisticBase):
    class Meta:
        db_table = 'user_statistic_total'
