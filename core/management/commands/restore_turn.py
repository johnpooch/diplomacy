from django.core.management.base import BaseCommand, CommandError

from core import models
from core.models.base import GameStatus


class Command(BaseCommand):

    @property
    def help(self):
        return 'Restore a game to a previous turn'

    def add_arguments(self, parser):
        parser.add_argument(
            'turn',
            type=int,
            help='ID of the turn to restore to (all later turns are archived).',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Skip prompt.',
        )

    def handle(self, *args, **options):
        turn_id = options['turn']
        noinput = options['noinput']
        try:
            turn = models.Turn.objects.get(id=turn_id)
        except models.Turn.DoesNotExist:
            raise CommandError(
                'Could not find a turn with the id "{}"'.format(turn_id)
            )

        if turn.current_turn:
            raise CommandError('Cannot restore to the current turn.')

        if turn.game.status != GameStatus.ACTIVE:
            raise CommandError('Cannot restore turn if game is not active.')

        current_turn = turn.game.get_current_turn()

        self.stdout.write('\n')
        self.stdout.write(
            'This will restore {} to {}. All later turns will be archived.'
            .format(current_turn, turn)
        )

        if not noinput:
            response = input('Are you sure you want to continue? [Y/n]: ')
            if response not in ['y', 'Y']:
                self.stdout.write('Exiting...')
                return

        restored_turn = turn.game.restore_turn(turn)
        self.stdout.write(
            '{} is now the current turn'
            .format(restored_turn)
        )
