from django.db import models


class VkGroup(models.Model):
    domain = models.CharField(max_length=150)

    def __str__(self):
        return self.domain

    class Meta:
        db_table = 'vk_group'
