from django.core.management import BaseCommand

# The class must be named Command, and subclass BaseCommand
from entities.models import VkGroup
from runner.fetching.statistic import update_rating


class Command(BaseCommand):
    # Show this when the user types help
    help = "My test command"

    def add_arguments(self, parser):
        parser.add_argument('group_id', type=int)

    # A command must define handle()
    def handle(self, *args, **options):
        group_id = options.get('group_id')
        group = VkGroup.objects.get(vk_id=group_id)
        update_rating(group.pk)
