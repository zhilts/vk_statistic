from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.generic import View

from entities.models import VkGroup
from entities.models import VkUser
from entities.models import VkUserStatisticTotal
from entities.models.Settings import SettingsKey
from entities.models.VkUserStatistic import VkUserStatisticPeriod
from helpers.datetime import end_of_period, current_period
from helpers.settings import rate_settings


class UserGroupOverview(View):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        group_id = kwargs.get('group_id')
        try:
            user = VkUser.objects.get(id=user_id)
            period = current_period()
            group = VkGroup.objects.get(vk_id=group_id)
            stats, _ = VkUserStatisticTotal.objects.get_or_create(group=group, user_id=user_id)
            period_stats, _ = VkUserStatisticPeriod.objects.get_or_create(group=group, user_id=user_id,
                                                                          period=period)

            stat_table = _build_table(stats=stats, period_stats=period_stats)

        except ObjectDoesNotExist:
            raise Http404

        return render(request, 'entities/group_user.html',
                      dict(user=user, stats=stat_table, group_id=group_id,
                           end_of_period=end_of_period().isoformat()))


def _build_table(stats, period_stats):
    rates = _get_rates()
    return [dict(
        title=_get_title(key, rates),
        tooltip=_get_tooltip(key, rates),
        total_stat=getattr(stats, key),
        period_stat=getattr(period_stats, key)
    ) for key in Row.ALL]


class Row:
    RATING = 'rating'
    TOTAL_SCORE = 'total_score'
    LIKES = 'likes'
    REPOSTS = 'reposts'
    LIKES_FOR_REPOSTS = 'likes_for_reposts'
    REPOSTS_FOR_REPOSTS = 'reposts_for_reposts'
    INVITES = 'invites'
    ALL = [RATING, TOTAL_SCORE, LIKES, REPOSTS, LIKES_FOR_REPOSTS, REPOSTS_FOR_REPOSTS, INVITES]


_tooltips = {
    Row.LIKES: lambda: _('For each like you will get'),
    Row.REPOSTS: lambda: _('For each repost you will get'),
    Row.LIKES_FOR_REPOSTS: lambda: _('For each like on your repost you will get'),
    Row.REPOSTS_FOR_REPOSTS: lambda: _('For each repost of your repost you will get'),
    Row.INVITES: lambda: _('For each new player from your invites you will get'),
}

_titles = {
    Row.RATING: lambda: _('Rating'),
    Row.TOTAL_SCORE: lambda: _('Karma'),
    Row.LIKES: lambda: _('Likes'),
    Row.REPOSTS: lambda: _('Reposts'),
    Row.LIKES_FOR_REPOSTS: lambda: _('Likes for Reposts'),
    Row.REPOSTS_FOR_REPOSTS: lambda: _('Reposts for Reposts'),
    Row.INVITES: lambda: _('Invited'),
}


def _tooltip_with_rate(tooltip, rate):
    return '{tooltip} +{rate} {tooltip_suffix}'.format(tooltip=tooltip, rate=rate,
                                                       tooltip_suffix=_('for your karma'))


def _get_tooltip(key, rates):
    return _tooltip_with_rate(_tooltips[key](), rates[key]) if key in _tooltips else None


def _get_title(key, rates):
    suffix = ' (x{rate})'.format(rate=rates[key]) if key in rates else ''
    return _titles[key]() + suffix


def _get_rates():
    rates = rate_settings()
    return dict(
        likes=rates[SettingsKey.RATE_LIKES],
        reposts=rates[SettingsKey.RATE_REPOSTS],
        likes_for_reposts=rates[SettingsKey.RATE_LIKES_FOR_REPOSTS],
        reposts_for_reposts=rates[SettingsKey.RATE_REPOSTS_FOR_REPOSTS],
        invites=rates[SettingsKey.RATE_INVITES],
    )
