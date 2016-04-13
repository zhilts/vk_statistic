# Create your views here.
from django.views.generic import ListView

from entities.models import VkGroup, VkPost, VkUser


class GroupListView(ListView):
    model = VkGroup


class PostListView(ListView):
    def get_queryset(self):
        return VkPost.objects.filter(group__vk_id=self.kwargs.get('group_id'))

class UserListView(ListView):
    def get_queryset(self):
        return VkUser.objects.filter(posts__group__vk_id=self.kwargs.get('group_id'))
