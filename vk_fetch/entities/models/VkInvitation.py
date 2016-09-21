from django.db import models

from entities.models import VkGroup
from entities.models import VkUser


class VkInvitation(models.Model):
    user = models.ForeignKey(VkUser, null=False)
    invited_by = models.ForeignKey(VkUser, null=False)
    group = models.ForeignKey(VkGroup, null=False)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vk_invite'
        unique_together = ('user', 'group')
