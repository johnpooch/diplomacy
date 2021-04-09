from django.core.management.base import BaseCommand, CommandError

from core import models
from core.models.base import GameStatus


class Command(BaseCommand):

    @property
    def help(self):
        return 'Show the turns of an active game'

    def add_arguments(self, parser):
        parser.add_argument(
            'game',
            type=str,
            help='Slug of the game to show.',
        )

    def handle(self, *args, **options):
        slug = options['game']
        try:
            game = models.Game.objects.get(slug=slug)
        except models.Game.DoesNotExist:
            raise CommandError(
                'Could not find a game with the slug "{}"'.format(slug)
            )

        if game.status == GameStatus.PENDING:
            raise CommandError('Cannot show turns for pending game.')
        self.stdout.write('\n' + str(game))
        for turn in game.turns.all():
            check = ' '
            if turn.processed:
                check = 'x'
            self.stdout.write('\t[{}] {}'.format(check, turn))
        self.stdout.write('\n')
