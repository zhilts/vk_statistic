from celery import chain
from django.core.management import BaseCommand

from runner.tasks import update_groups, update_users


class Command(BaseCommand):
    def handle(self, *args, **options):
        return chain([update_groups.si(), update_users.si()]).apply_async().get()
