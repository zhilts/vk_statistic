from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Value, Case, When, BooleanField
from django.db.models.functions import Concat
from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import View
from django.utils.translation import ugettext as _

from entities.models import VkGroup, VkPost, VkUser, VkUserStatisticTotal
from entities.models.RunPeriod import RunPeriod
from entities.models.Settings import SettingsKey
from entities.models.VkUserStatistic import VkUserStatisticPeriod
from helpers.datetime import start_of_current_period, end_of_period
from helpers.settings import rate_settings
from runner.tasks import add_invite


class GroupListView(ListView):
    model = VkGroup


class PostListView(ListView):
    def get_queryset(self):
        return VkPost.objects.filter(group__vk_id=self.kwargs.get('group_id'))


class UserListView(ListView):
    def get_queryset(self):
        params = self.request.GET
        page = int(params.get('page', 0))
        limit = int(params.get('limit', 10))
        start = page * limit
        end = start + limit

        qs = VkUser.objects \
                 .filter(liked_posts__group__vk_id=self.kwargs.get('group_id')) \
                 .distinct() \
                 .order_by('last_name', 'first_name', 'id')[start:end]
        return qs


class UserLikesListView(ListView):
    def get_queryset(self):
        post = VkPost.objects.get(pk=self.kwargs.get('post_id'))
        return post.likes.all()


class BaseTopView(ListView):
    template_name = 'top_ten.html'

    def __init__(self, *args, **kwargs):
        super(BaseTopView, self).__init__(*args, **kwargs)
        self.base_query = None
        self.group_id = None

    def get_context_data(self, **kwargs):
        context = super(BaseTopView, self).get_context_data(**kwargs)
        context['group_id'] = self.group_id

        context['end_of_period'] = end_of_period().isoformat()
        return context

    # todo: move to middleware
    def update_invites(self, viewer_id, params):
        referrer = params.get('referrer', '')
        if referrer == 'request':
            user_id = int(params.get('user_id'))
            group_id = self.group_id
            add_invite.delay(group_id=group_id, viewer_id=viewer_id, user_id=user_id)

    def get_queryset(self):
        viewer_id = int(self.request.GET.get('viewer_id', 0))
        self.group_id = int(self.kwargs.get('group_id'))
        self.update_invites(viewer_id, self.request.GET)

        group = VkGroup.objects.get(vk_id=self.group_id)
        qs = self.base_query \
                 .select_related('user') \
                 .filter(group=group) \
                 .exclude(total_score=0) \
                 .annotate(current_user=Case(When(user_id=viewer_id, then=True),
                                             default=False,
                                             output_field=BooleanField())) \
                 .annotate(screen_name=Concat('user__last_name', Value(' '), 'user__first_name')) \
                 .order_by('-current_user', 'rating', 'screen_name')[0:10]

        sort = sorted(qs, key=lambda u: (u.rating, u.screen_name))
        return sort


class UserTopTenView(BaseTopView):
    def __init__(self, *args, **kwargs):
        super(UserTopTenView, self).__init__(*args, **kwargs)
        self.base_query = VkUserStatisticTotal.objects


class UserTopTenPeriod(BaseTopView):
    def get_queryset(self):
        period_id = self.kwargs.get('period_id', 0)
        self.base_query = VkUserStatisticPeriod.objects.filter(period_id=period_id)
        return super(UserTopTenPeriod, self).get_queryset()


def current_period():
    current_period_start = start_of_current_period()
    period, _ = RunPeriod.objects.get_or_create(timestamp=current_period_start)
    return period


class CurrentPeriodTopTen(View):
    def get(self, request, *args, **kwargs):
        view = UserTopTenPeriod.as_view()
        kwargs['period_id'] = current_period().pk
        return view(request, *args, **kwargs)


class GroupPeriodsView(ListView):
    template_name = 'entities/group_periods.html'

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        return RunPeriod.objects.filter(vkuserstatisticperiod__group__vk_id=group_id).distinct().order_by('timestamp')

    def get_context_data(self, **kwargs):
        context = super(GroupPeriodsView, self).get_context_data(**kwargs)
        group = VkGroup.objects.get(vk_id=self.kwargs.get('group_id'))
        context['group'] = group
        return context


def get_rates():
    rates = rate_settings()
    return dict(
        likes=rates[SettingsKey.RATE_LIKES],
        reposts=rates[SettingsKey.RATE_REPOSTS],
        likes_for_reposts=rates[SettingsKey.RATE_LIKES_FOR_REPOSTS],
        reposts_for_reposts=rates[SettingsKey.RATE_REPOSTS_FOR_REPOSTS],
        invites=rates[SettingsKey.RATE_INVITES],
    )


def title_with_rate(title, rate):
    return '{title} (x{rate})'.format(title=_(title), rate=rate)


def get_titles(rates):
    return _('Rating'), \
           _('Karma'), \
           title_with_rate('Likes', rates['likes']), \
           title_with_rate('Reposts', rates['reposts']), \
           title_with_rate('Likes for Reposts', rates['likes_for_reposts']), \
           title_with_rate('Reposts for Reposts', rates['reposts_for_reposts']), \
           title_with_rate('Invited', rates['invites'])


def tooltip_with_rate(tooltip, rate):
    return '{tooltip} +{rate} {tooltip_suffix}'.format(tooltip=_(tooltip), rate=rate,
                                                       tooltip_suffix=_('for your karma'))


def get_tooltips(rates):
    return None, \
           None, \
           tooltip_with_rate('For each like you will get', rates['likes']), \
           tooltip_with_rate('For each repost you will get', rates['reposts']), \
           tooltip_with_rate('For each like on your repost you will get', rates['likes_for_reposts']), \
           tooltip_with_rate('For each repost of your repost you will get', rates['reposts_for_reposts']), \
           tooltip_with_rate('For each new player from your invites you will get', rates['invites'])


def build_table(stats, period_stats):
    rates = get_rates()
    titles = get_titles(rates)
    tooltips = get_tooltips(rates)
    keys = ['rating', 'total_score', 'likes', 'reposts', 'likes_for_reposts', 'reposts_for_reposts', 'invites']
    return [dict(
        title=titles[index],
        tooltip=tooltips[index],
        total_stat=getattr(stats, key),
        period_stat=getattr(period_stats, key)) for
            (index, key) in enumerate(keys)]


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

            stat_table = build_table(stats=stats, period_stats=period_stats)

        except ObjectDoesNotExist:
            raise Http404

        return render(request, 'entities/group_user.html',
                      dict(user=user, stats=stat_table, group_id=group_id,
                           end_of_period=end_of_period().isoformat()))
