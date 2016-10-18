from datetime import datetime, timedelta
from django.utils import timezone

from entities.models.Settings import SettingsKey
from helpers.settings import period_settings


def get_now():
    return datetime.now(timezone.utc)


def start_of_an_hour(ts):
    return ts.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)


def start_of_day(ts):
    return start_of_an_hour(ts).replace(hour=0)


def start_of_week(ts):
    current_date = start_of_day(ts)
    return current_date - timedelta(days=current_date.weekday())


def start_of_current_period(now=None):
    now = now or get_now()
    settings = period_settings()
    run_start = settings[SettingsKey.PERIOD_START]
    run_period = settings[SettingsKey.PERIOD_DURATION]
    return run_start + int((now - run_start) / run_period) * run_period


def end_of_period(now=None):
    now = now or get_now()
    settings = period_settings()
    start_of_the_period = start_of_current_period(now)
    run_period = settings[SettingsKey.PERIOD_DURATION]
    return start_of_the_period + run_period
