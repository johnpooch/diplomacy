from datetime import datetime
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.timezone import make_aware

from core import models
from core.models.base import GameStatus


class Command(BaseCommand):

    @property
    def help(self):
        return 'Set when the current turn of a game will be processed.'

    def add_arguments(self, parser):
        parser.add_argument(
            'game',
            type=str,
            help=(
                'The slug of the game to be updated.'
            )
        )
        parser.add_argument(
            'datetime',
            type=str,
            help=(
                'The date/time that the game turn will be processed. Date '
                'time should be in the format \'YYYY-MM-DD HH:MM:SS\'.'
            )
        )
        parser.add_argument(
            '--timezone',
            type=str,
            default='UTC',
            help=(
                'The timezone for the given datetime. Defaults to UTC.'
            )
        )

    def handle(self, *args, **options):
        slug = options['game']
        date_string = options['datetime']
        tz = options['timezone']
        now = timezone.now()

        try:
            dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            dt = make_aware(dt, timezone=pytz.timezone(tz))
        except ValueError as e:
            raise CommandError(str(e))

        if now >= dt:
            raise CommandError(
                'datetime must be a time in the future.'
            )

        try:
            game = models.Game.objects.get(slug=slug, status=GameStatus.ACTIVE)
        except models.Game.DoesNotExist:
            raise CommandError(
                'Invalid slug. Must be the slug of a live game.'
            )

        current_turn = game.get_current_turn()
        models.TurnEnd.objects.filter(turn=current_turn).delete()
        turn_end = models.TurnEnd.objects.new(current_turn, dt)
        self.stdout.write(repr(turn_end))
