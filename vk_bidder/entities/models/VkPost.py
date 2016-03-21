from django.db import models

from entities.models import VkGroup


class VkPost(models.Model):
    post_id = models.IntegerField()
    group = models.ForeignKey(VkGroup)

    text = models.TextField()
    likes_count = models.IntegerField()
    reposts_count = models.IntegerField()

    def __str__(self):
        return '{group}: likes={likes}, reposts={reposts}; text={text}' \
            .format(
                group=self.group,
                likes=self.likes_count,
                reposts=self.reposts_count,
                text=self.text[:20]
        )

    class Meta:
        db_table = 'vk_post'
        unique_together = ('group', 'post_id')
