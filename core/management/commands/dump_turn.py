import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core import models


class Command(BaseCommand):

    @property
    def help(self):
        return 'Dump a turn\'s data and related data into a fixture directory.'

    def add_arguments(self, parser):
        parser.add_argument(
            'id',
            type=int,
            help='ID of the game to dump.',
        )
        parser.add_argument(
            'location',
            type=str,
            help='Directory to dump data in.',
        )

    # TODO dry
    def get_model_identifier(self, model):
        """
        Gets model string identifier for model, e.g. 'core.Game'.

        Args:
            * `model` - `Model` - Any model class.

        Returns:
            `str`
        """
        return '.'.join([model._meta.app_label, model._meta.object_name])

    # TODO dry
    def dump_model(self, model, ids, location):
        """
        Dump data for a given model and ids in the specified location.

        Args:
            * `model` - `Model` - Any model class.
            * `ids` - `list` - Ids of instances to be dumped.
            * `location` - `str` - File path relative to `game_dir_name` where
              data will be saved.
        """
        model_identifier = self.get_model_identifier(model)
        call_command(
            'dumpdata',
            model_identifier,
            '--pks',
            ','.join([str(i) for i in ids]),
            '--indent',
            '4',
            '--output',
            location,
        )

    @transaction.atomic
    def handle(self, *args, **options):
        location = '/'.join([settings.BASE_DIR, options['location']])

        if not os.path.isdir(location):
            raise CommandError(f'"{location}" not found.')

        turn = models.Turn.objects.get(id=options['id'])
        game = turn.game

        game_location = '/'.join([location, 'game.json'])
        self.dump_model(models.Game, [turn.game.id], game_location)

        created_by_location = '/'.join([location, 'created_by.json'])
        self.dump_model(User, [turn.game.created_by.id], created_by_location)

        turn_location = '/'.join([location, 'turn.json'])
        self.dump_model(models.Turn, [turn.id], turn_location)

        participant_ids = game.participants.all().values_list('id', flat=True)
        participants_location = '/'.join([location, 'participants.json'])
        self.dump_model(User, participant_ids, participants_location)

        pieces = game.pieces.all()
        pieces_ids = pieces.values_list('id', flat=True)
        piece_location = '/'.join([location, 'piece.json'])
        self.dump_model(models.Piece, pieces_ids, piece_location)

        piece_state_ids = turn.piecestates.all().values_list('id', flat=True)
        piece_state_location = '/'.join([location, 'piece_state.json'])
        self.dump_model(models.PieceState, piece_state_ids, piece_state_location)

        nation_state_ids = turn.nationstates.all().values_list('id', flat=True)
        nation_state_location = '/'.join([location, 'nation_state.json'])
        self.dump_model(models.NationState, nation_state_ids, nation_state_location)

        territory_state_ids = turn.territorystates.all().values_list('id', flat=True)
        territory_state_location = '/'.join([location, 'territory_state.json'])
        self.dump_model(models.TerritoryState, territory_state_ids, territory_state_location)

        order_ids = turn.orders.all().values_list('id', flat=True)
        order_location = '/'.join([location, 'order.json'])
        self.dump_model(models.Order, order_ids, order_location)
