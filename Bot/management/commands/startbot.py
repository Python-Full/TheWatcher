from django.core.management.base import BaseCommand, CommandError

from Bot.R2D2 import start
from Bot.models import Client


class Command(BaseCommand):
    help = 'Does some magical work'

    def handle(self, *args, **options):
        """ Do your work here """
        start()
        self.stdout.write('There are {} things!'.format(Client.objects.count()))
