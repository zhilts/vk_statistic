from datetime import timedelta, datetime

import pytz

from entities.models.Settings import Settings, SettingsKey


def str_to_datetime(str_datetime):
    return pytz.UTC.localize(datetime.strptime(str_datetime, '%d-%m-%Y_%H-%M'))


def settings_to_dict(settings):
    return dict(map(lambda s: (s.pk, s.value), settings))


def update_dict(d, key, default, cast_fn=lambda x: x):
    d[key] = cast_fn(d.get(key, default))


def rate_settings():
    rate_keys = [
        SettingsKey.RATE_LIKES,
        SettingsKey.RATE_REPOSTS,
        SettingsKey.RATE_LIKES_FOR_REPOSTS,
        SettingsKey.RATE_REPOSTS_FOR_REPOSTS,
        SettingsKey.RATE_INVITES,
    ]
    settings = Settings.objects.filter(pk__in=rate_keys)
    settings_dict = settings_to_dict(settings)
    for key in rate_keys:
        update_dict(settings_dict, key, 1, int)
    return settings_dict


def period_settings():
    settings = Settings.objects.filter(pk__in=[SettingsKey.PERIOD_DURATION, SettingsKey.PERIOD_START])

    settings_dict = settings_to_dict(settings)

    update_dict(settings_dict, SettingsKey.PERIOD_START, '1-10-2016_0-0', str_to_datetime)
    update_dict(settings_dict, SettingsKey.PERIOD_DURATION, 72, lambda v: timedelta(hours=int(v)))

    return settings_dict
