from django.db import models


class SettingsKey:
    RATE_LIKES = 'rates.likes'
    RATE_REPOSTS = 'rates.reposts'
    RATE_LIKES_FOR_REPOSTS = 'rates.likesForReposts'
    RATE_REPOSTS_FOR_REPOSTS = 'rates.repostsForReposts'
    RATE_INVITES = 'rates.invites'
    RATE_POSTS = 'rates.ownPosts'
    RATE_LIKES_FOR_OWN_POSTS = 'rates.likesForOwnPosts'
    RATE_REPOSTS_FOR_OWN_POSTS = 'rates.repostsForOwnPosts'
    PERIOD_DURATION = 'period.duration'
    PERIOD_START = 'period.start'


keys_choices = ((value, value) for key, value in SettingsKey.__dict__.items() if key.isupper())


class Settings(models.Model):
    key = models.CharField(primary_key=True, choices=keys_choices, max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return '{key}: {value}'.format(key=self.key, value=self.value)

    class Meta:
        db_table = 'settings'
