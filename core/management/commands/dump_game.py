import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core import models


class Command(BaseCommand):

    @property
    def help(self):
        return 'Dump a game\'s data into a fixture directory.'

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
        parser.add_argument(
            'game_dir_name',
            type=str,
            help='Name of directory which will be created for fixture.',
        )

    def get_model_identifier(self, model):
        """
        Gets model string identifier for model, e.g. 'core.Game'.

        Args:
            * `model` - `Model` - Any model class.

        Returns:
            `str`
        """
        return '.'.join([model._meta.app_label, model._meta.object_name])

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
        directory = '/'.join([settings.BASE_DIR, options['location']])
        game_dir_name = options['game_dir_name']

        if not os.path.isdir(directory):
            raise CommandError(f'"{directory}" not found.')

        # ensure game directory doesn't already exist
        location = '/'.join([directory, game_dir_name])
        if os.path.exists(location):
            raise CommandError(
                f'"{directory}" already has a file or directory called '
                f'{game_dir_name}.'
            )
        os.makedirs(location)

        game = models.Game.objects.get(id=options['id'])

        variant = game.variant

        nations = variant.nations.all()
        nation_location = '/'.join([location, 'nation.json'])
        nation_ids = nations.values_list('id', flat=True)
        self.dump_model(models.Nation, nation_ids, nation_location)

        territories = variant.territories.all()
        territory_location = '/'.join([location, 'territory.json'])
        territory_ids = territories.values_list('id', flat=True)
        self.dump_model(models.Territory, territory_ids, territory_location)

        named_coasts = models.NamedCoast.objects.filter(
            parent__in=territories
        )
        named_coast_location = '/'.join([location, 'named_coast.json'])
        named_coast_ids = named_coasts.values_list('id', flat=True)
        self.dump_model(models.NamedCoast, named_coast_ids, named_coast_location)

        game_location = '/'.join([location, 'game.json'])
        self.dump_model(models.Game, [game.id], game_location)

        turns = game.turns.all()
        turn_ids = turns.values_list('id', flat=True)
        turn_location = '/'.join([location, 'turn.json'])
        self.dump_model(models.Turn, turn_ids, turn_location)

        pieces = game.pieces.all()
        pieces_ids = pieces.values_list('id', flat=True)
        piece_location = '/'.join([location, 'piece.json'])
        self.dump_model(models.Piece, pieces_ids, piece_location)

        piece_states = models.PieceState.objects.filter(
            piece_id__in=pieces_ids
        )
        piece_states_ids = piece_states.values_list('id', flat=True)
        piece_state_location = '/'.join([location, 'piece_state.json'])
        self.dump_model(models.PieceState, piece_states_ids, piece_state_location)

        nation_states = models.NationState.objects.filter(
            turn_id__in=turn_ids
        )
        nation_states_ids = nation_states.values_list('id', flat=True)
        nation_state_location = '/'.join([location, 'nation_state.json'])
        self.dump_model(models.NationState, nation_states_ids, nation_state_location)

        territory_states = models.TerritoryState.objects.filter(
            turn_id__in=turn_ids
        )
        territory_states_ids = territory_states.values_list('id', flat=True)
        territory_state_location = '/'.join([location, 'territory_state.json'])
        self.dump_model(models.TerritoryState, territory_states_ids, territory_state_location)
