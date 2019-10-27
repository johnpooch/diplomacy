from django.test import TestCase

from core import models
from core.utils.piece import army, fleet
from core.models.base import CommandType


class InitialGameStateTestCase(TestCase):
    """
    """
    def setUp(self):
        # Game State
        self.game = models.Game.objects.create(
            name='test game',
        )
        self.phase = models.Phase.objects.create(
            season='S',
            type='O',
        )
        self.turn = models.Turn.objects.create(
            year=1900,
            phase=self.phase,
            game=self.game,
            current_turn=True,
        )


class TerritoriesMixin:

    def initialise_territories(self):
        """
        Makes all territories available as attributes, e.g. ``self.paris``.
        """
        for territory in models.Territory.objects.all():
            name = territory.name.lower().replace(' ', '_').replace('.', '')
            setattr(self, name, territory)


class HelperMixin:

    def initialise_nations(self):
        """
        Makes all nations available as attributes, e.g. ``self.england``.
        Makes 'Austria-Hungary' available as 'austria'.
        """
        for nation in models.Nation.objects.all():
            if nation.name == 'Austria-Hungary':
                name = 'austria'
            else:
                name = nation.name.lower()
            setattr(self, name, nation)

    def initialise_orders(self):
        """
        """
        for nation in models.Nation.objects.all():
            if nation.name == 'Austria-Hungary':
                name = 'austria'
            else:
                name = nation.name.lower()
            order = models.Order.objects.create(
                nation=nation,
                turn=self.turn,
            )
            setattr(self, name + '_order', order)

    def initialise_territories(self):
        """
        Makes all territories available as attributes, e.g. ``self.paris``.
        """
        for territory in models.Territory.objects.all():
            name = territory.name.lower().replace(' ', '_').replace('.', '')
            setattr(self, name, territory)

    def initialise_named_coasts(self):
        """
        Makes all named coasts available as attributes, e.g. ``self.spain_nc``.
        """
        for named_coast in models.NamedCoast.objects.all():
            name = named_coast.parent.name + '_' + named_coast.map_abbreviation
            setattr(self, name, named_coast)

    def set_piece_territory(self, piece, territory, named_coast=None):
        """
        """
        piece.territory = territory
        piece.named_coast = named_coast
        piece.save()

    def hold(self, piece, source):
        """
        """
        return models.Command(
            source=source,
            piece=piece,
            order=self.order,
            type=CommandType.HOLD,
        )

    def move(self, piece, source, target, target_coast=None):
        """
        Helper to create a move command.
        """
        return models.Command(
            piece=piece,
            source=source,
            target=target,
            order=self.order,
            target_coast=target_coast,
            type=CommandType.MOVE,
        )

    def support(self, piece, source, aux, target):
        """
        """
        return models.Command(
            piece=piece,
            source=source,
            target=target,
            aux=aux,
            order=self.order,
            type=CommandType.SUPPORT,
        )

    def convoy(self, piece, source, target, aux):
        """
        """
        return models.Command(
            piece=piece,
            source=source,
            target=target,
            aux=aux,
            order=self.order,
            type=CommandType.CONVOY,
        )

    def build(self, target, piece_type, target_coast=None):
        """
        """
        return models.Command(
            target=target,
            target_coast=target_coast,
            piece_type=piece_type,
            order=self.order,
            type=CommandType.BUILD
        )

    @staticmethod
    def refresh_all(items):
        """
        """
        try:
            [i.refresh_from_db() for i in items]
        except AttributeError:
            pass


def command_and_piece(nation, piece_type, source, command_type, aux=None,
                      target=None, target_coast=None, via_convoy=False):
    """
    Helper to easily create piece and command.
    """
    if piece_type == 'army':
        p = army(nation, source)
    elif piece_type == 'fleet':
        p = fleet(nation, source)
    else:
        raise ValueError(f'Unrecognized piece type: {piece_type}')

    order = models.Order.objects.get(nation=nation)
    models.Command.objects.create(
        piece=p,
        source=source,
        target=target,
        target_coast=target_coast,
        aux=aux,
        order=order,
        type=command_type,
        via_convoy=via_convoy,
    )
    return p
