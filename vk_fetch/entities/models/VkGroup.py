from django.db import models


class VkGroup(models.Model):
    vk_id = models.IntegerField(null=True)
    domain = models.CharField(max_length=150)
    active = models.BooleanField(null=False, default=True)

    @property
    def owner_id(self):
        return -self.vk_id

    def __str__(self):
        return self.domain

    class Meta:
        db_table = 'vk_group'
