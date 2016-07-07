from django.db import models

from entities.models.VkPost import VkPost
from entities.models.VkUser import VkUser


class VkRepost(models.Model):
    id = models.AutoField(primary_key=True)
    vk_id = models.IntegerField(null=False, blank=False)
    post = models.ForeignKey(VkPost, null=False)
    user = models.ForeignKey(VkUser, null=False)
    likes = models.IntegerField(default=0, null=False)
    reposts = models.IntegerField(default=0, null=False)

    class Meta:
        db_table = 'vk_repost'
        unique_together = ('post', 'vk_id', 'user')
