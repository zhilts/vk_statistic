from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Value, Case, When, BooleanField
from django.db.models.functions import Concat
from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import View
from requests import session

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


def get_viewer_id():
    return getattr(session, 'user_id', 0)


class BaseTopView(ListView):
    template_name = 'top_ten.html'

    def __init__(self, *args, **kwargs):
        super(BaseTopView, self).__init__(*args, **kwargs)
        self.base_query = None
        self.group_id = None

    def get_context_data(self, **kwargs):
        context = super(BaseTopView, self).get_context_data(**kwargs)
        context['group_id'] = self.group_id
        context['current_user_id'] = get_viewer_id()
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
        viewer_id = get_viewer_id()
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


class CurrentPeriodTopTen(View):
    def get(self, request, *args, **kwargs):
        view = UserTopTenPeriod.as_view()
        current_period_start = start_of_current_period()
        period, _ = RunPeriod.objects.get_or_create(timestamp=current_period_start)
        kwargs['period_id'] = period.pk
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
        context['current_user_id'] = getattr(session, 'user_id', 0)
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


class UserGroupOverview(View):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        group_id = kwargs.get('group_id')
        try:
            user = VkUser.objects.get(id=user_id)
            stats, _ = VkUserStatisticTotal.objects.get_or_create(group__vk_id=group_id, user_id=user_id)
        except ObjectDoesNotExist:
            raise Http404

        return render(request, 'entities/group_user.html',
                      dict(user=user, stats=stats, group_id=group_id, current_user_id=user_id, rates=get_rates(),
                           end_of_period=end_of_period().isoformat()))
