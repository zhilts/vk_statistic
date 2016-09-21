# Create your views here.
from django.db.models import F, Value, Case, When, BooleanField
from django.db.models.functions import Concat
from django.views.generic import ListView

from entities.models import VkGroup, VkPost, VkUser, VkUserStatisticTotal
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


class UserTopTenView(ListView):
    def __init__(self, *args, **kwargs):
        super(UserTopTenView, self).__init__(*args, **kwargs)
        self.template_name = 'entities/top_ten.html'

    def update_invites(self, viewer_id, params):
        referrer = params.get('referrer', '')
        if referrer == 'request':
            user_id = int(params.get('user_id'))
            group_id = self.kwargs.get('group_id')
            add_invite.delay(group_id=group_id, viewer_id=viewer_id, user_id=user_id)

    def get_queryset(self):
        viewer_id = int(self.request.GET.get('viewer_id', -1))
        self.update_invites(viewer_id, self.request.GET)

        group = VkGroup.objects.get(vk_id=self.kwargs.get('group_id'))
        qs = VkUserStatisticTotal.objects \
                 .select_related('user') \
                 .filter(group=group) \
                 .annotate(current_user=Case(When(user_id=viewer_id, then=True),
                                             default=False,
                                             output_field=BooleanField())) \
                 .annotate(screen_name=Concat('user__last_name', Value(' '), 'user__first_name')) \
                 .order_by('-current_user', 'rating', 'screen_name')[0:10]

        sort = sorted(qs, key=lambda u: (u.rating, u.screen_name))
        return sort
