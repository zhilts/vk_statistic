from django.db import models

from entities.models.VkGroup import VkGroup
from entities.models.VkUser import VkUser
from helpers.datetime import create_datetime


class VkPost(models.Model):
    post_id = models.IntegerField()
    group = models.ForeignKey(VkGroup)

    text = models.TextField()
    likes_count = models.IntegerField()
    reposts_count = models.IntegerField()

    from_id = models.IntegerField(default=0)
    author = models.ForeignKey(VkUser, null=True)

    date = models.DateTimeField(default=create_datetime(2016, 11, 1))

    likes = models.ManyToManyField(VkUser, related_name='liked_posts')

    @property
    def owner_id(self):
        return self.group.owner_id

    def __str__(self):
        return '{group}: likes={likes}, reposts={reposts}; text={text}'.format(
            group=self.group,
            likes=self.likes_count,
            reposts=self.reposts_count,
            text=self.text[:20]
        )

    class Meta:
        db_table = 'vk_post'
        unique_together = ('group', 'post_id')
