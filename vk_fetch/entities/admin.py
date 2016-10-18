from django import forms
from django.contrib import admin

from entities.models import VkGroup, VkPost, VkUser
from entities.models.Settings import Settings

admin.site.register(VkGroup)
admin.site.register(VkPost)
admin.site.register(Settings)


class VkUserAdminForm(forms.ModelForm):
    posts = forms.ModelMultipleChoiceField(
        VkPost.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Posts', False),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(VkUserAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['posts'] = self.instance.posts.values_list('pk', flat=True)

    def save(self, *args, **kwargs):
        instance = super(VkUserAdminForm, self).save(*args, **kwargs)
        if instance.pk:
            instance.posts.clear()
            instance.posts.add(*self.cleaned_data['posts'])
        return instance


class VkUserAdmin(admin.ModelAdmin):
    form = VkUserAdminForm


admin.site.register(VkUser, VkUserAdmin)
