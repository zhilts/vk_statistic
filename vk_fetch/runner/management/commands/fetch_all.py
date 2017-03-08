from django.core.management import BaseCommand

from runner.tasks import fetch_all


class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_all.apply_async().get()
