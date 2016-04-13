from django.contrib import admin

from entities.models import VkGroup, VkPost, VkUser

admin.site.register(VkGroup)
admin.site.register(VkPost)
admin.site.register(VkUser)
