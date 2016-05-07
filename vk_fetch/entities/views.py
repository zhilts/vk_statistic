# Create your views here.
from django.db.models import Count, F
from django.views.generic import ListView

from entities.models import VkGroup, VkPost, VkUser


class GroupListView(ListView):
    model = VkGroup


class PostListView(ListView):
    def get_queryset(self):
        return VkPost.objects.filter(group__vk_id=self.kwargs.get('group_id'))


class UserListView(ListView):

    def get_queryset(self):
        viewer_id = self.kwargs.get('viewer_id', None)

        qs = VkUser.objects \
            .filter(liked_posts__group__vk_id=self.kwargs.get('group_id')) \
            .annotate(like_count=Count('id')) \
            .annotate(total_score=F('like_count')) \
            .distinct()
        if viewer_id is not None:
            return qs.order_by('-total_score')
        else:
            return qs.order_by('last_name', 'first_name')


class UserLikesListView(ListView):
    def get_queryset(self):
        post = VkPost.objects.get(pk=self.kwargs.get('post_id'))
        return post.likes.all()
