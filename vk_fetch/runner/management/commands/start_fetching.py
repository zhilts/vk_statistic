from django.core.management import BaseCommand

# The class must be named Command, and subclass BaseCommand
from runner.fetching import process_all


class Command(BaseCommand):
    # Show this when the user types help
    help = "My test command"

    # A command must define handle()
    def handle(self, *args, **options):
        process_all()
