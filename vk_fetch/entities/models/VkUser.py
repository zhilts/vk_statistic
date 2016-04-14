from django.db import models


class VkUser(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    photo_50 = models.URLField(null=True)

    class Meta:
        db_table = 'vk_user'
