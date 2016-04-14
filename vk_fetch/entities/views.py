# Create your views here.
from django.db.models import Count
from django.views.generic import ListView

from entities.models import VkGroup, VkPost, VkUser


class GroupListView(ListView):
    model = VkGroup


class PostListView(ListView):
    def get_queryset(self):
        return VkPost.objects.filter(group__vk_id=self.kwargs.get('group_id'))


class UserListView(ListView):
    def get_queryset(self):
        qs = VkUser.objects \
            .filter(posts__group__vk_id=self.kwargs.get('group_id')) \
            .annotate(like_count=Count('id')) \
            .distinct() \
            .order_by('last_name', 'first_name')
        print(qs.count())
        return qs


class UserLikesListView(ListView):
    def get_queryset(self):
        post = VkPost.objects.get(pk=self.kwargs.get('post_id'))
        return post.likes.all()
