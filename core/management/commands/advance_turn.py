import json

from django.core.management.base import BaseCommand, CommandError

from core import models
from core.game import process_turn
from core.models.base import GameStatus
from . import DiplomacyManagementCommandMixin


class Command(BaseCommand, DiplomacyManagementCommandMixin):

    @property
    def help(self):
        return 'Restore a game to a previous turn'

    def add_arguments(self, parser):
        parser.add_argument(
            'game',
            type=str,
            help='Slug of the game to advance',
        )
        parser.add_argument(
            '--no_input',
            action='store_true',
            help='Skip prompt.',
        )
        parser.add_argument(
            '--dry_run',
            action='store_true',
            help='Do not advance turn - show outcome of adjudicator.',
        )

    def handle(self, *args, **options):
        slug = options['game']
        self.noinput = options['no_input']
        dry_run = options['dry_run']
        try:
            game = models.Game.objects.get(slug=slug)
        except models.Game.DoesNotExist:
            raise CommandError(
                'Could not find a game with the slug "{}"'.format(slug)
            )

        if game.status != GameStatus.ACTIVE:
            raise CommandError(
                'Cannot advance turn on an inactive game'
            )

        turn = game.get_current_turn()

        if turn.game.status != GameStatus.ACTIVE:
            raise CommandError('Cannot restore turn if game is not active.')

        if not turn.ready_to_process:
            self.stdout.write('Not all nations have finalized their orders\n')

        self.prompt()

        result = process_turn(turn, dry_run)
        if dry_run:
            pretty_output = json.dumps(result, sort_keys=True, indent=4)
            self.stdout.write(pretty_output)
