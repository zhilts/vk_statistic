from django.db import models


class VkUser(models.Model):
    class Meta:
        abstract = True