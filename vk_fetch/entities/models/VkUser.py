from django.db import models


class VkUser(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        db_table = 'vk_user'
