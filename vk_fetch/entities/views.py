# Create your views here.
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.views.generic import ListView

from entities.models import VkGroup, VkPost, VkUser, VkUserStatisticTotal


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
    def get_queryset(self):
        group = VkGroup.objects.get(vk_id=self.kwargs.get('group_id'))
        qs = VkUserStatisticTotal.objects \
                 .select_related('user') \
                 .filter(group=group) \
                 .annotate(total_score=F('likes')) \
                 .annotate(screen_name=Concat('user__last_name', Value(' '), 'user__first_name')) \
                 .order_by('-total_score', 'screen_name')[0:10]
        return qs
