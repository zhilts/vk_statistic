from datetime import datetime, timedelta
from django.utils import timezone

from django.conf import settings


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
    run_start = settings.RUN_START
    run_period = settings.RUN_PERIOD
    return run_start + int((now - run_start) / run_period) * run_period
