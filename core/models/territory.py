from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from core.models import Piece
from core.models.base import OrderType, PerTurnModel, PieceType, \
    TerritoryType
from core.models.mixins.decisions import HoldStrength


class Territory(models.Model, HoldStrength):
    """
    Represents an area in the game map that can be occupied.
    """
    name = models.CharField(
        max_length=50,
        null=False,
    )
    controlled_by_initial = models.ForeignKey(
        'Nation',
        on_delete=models.CASCADE,
        null=True,
        related_name='initially_controlled_territories',
    )
    variant = models.ForeignKey(
        'Variant',
        null=False,
        on_delete=models.CASCADE,
        related_name='territories',
    )
    nationality = models.ForeignKey(
        'Nation',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='national_territories',
    )
    neighbours = models.ManyToManyField(
        'self',
        symmetrical=True,
        blank=True,
    )
    shared_coasts = models.ManyToManyField(
        'self',
        symmetrical=True,
    )
    type = models.CharField(
        max_length=10,
        choices=TerritoryType.CHOICES,
        null=False
    )
    coastal = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "territory"

    # TODO add validation so that sea territories can't be controlled.

    def __str__(self):
        return self.name.title()

    def state(self, turn):
        return self.territory_states.get(turn=turn)

    def standoff_occured_on_previous_turn(self):
        # TODO do this when phases/logs are properly handled
        pass

    def adjacent_to(self, territory):
        return territory in self.neighbours.all()

    def shares_coast_with(self, territory):
        return territory in self.shared_coasts.all()

    def get_piece(self):
        """
        Return the piece if it exists in the territory. If no piece exists
        in the territory, return False. If more than one piece exists in the
        territory, throw an error.
        """
        if self.pieces.all().count() == 1:
            return self.pieces.all()[0]
        if self.pieces.all().count() > 1:
            raise ValueError((
                f"More than one piece exists in {self}. There should never be "
                "more than one piece in a territory except when retreating or "
                "disbanding."))
        return False

    def occupied(self):
        """
        Determine whether a piece exists in a territory.
        """
        try:
            return bool(self.piece)
        except Piece.DoesNotExist:
            return False

    def friendly_piece_exists(self, nation):
        """
        Determine whether a piece belonging to ``nation`` exists in a
        territory.
        """
        try:
            return self.piece.nation == nation
        except Piece.DoesNotExist:
            return False

    def accessible_by_piece_type(self, piece):
        """
        Armies cannot enter sea territories. Fleets cannot enter non-coastal
        land territories.
        """
        if piece.type == PieceType.ARMY:
            return self.type == TerritoryType.LAND
        return (self.type == TerritoryType.SEA) or self.coastal

    def has_supply_center(self):
        try:
            return bool(self.supply_center)
        except ObjectDoesNotExist:
            return False

    @property
    def is_land(self):
        return self.type == TerritoryType.LAND

    @property
    def is_sea(self):
        return self.type == TerritoryType.SEA

    @property
    def is_inland(self):
        return self.is_land and not self.coastal

    @property
    def is_complex(self):
        return self.named_coasts.all().exists()

    @property
    def attacking_pieces(self):
        """
        Helper method to get all pieces which are moving into this territory.
        """
        return Piece.objects.filter(
            command__target=self,
            command__type=OrderType.MOVE
        )

    def foreign_attacking_pieces(self, nation):
        """
        Helper method to get all pieces which are moving into this territory
        who do not belong to ``nation``.
        """
        return self.attacking_pieces.exclude(nation=nation)

    def other_attacking_pieces(self, piece):
        # TODO test
        """
        Helper method to get all pieces which are moving into this territory
        not including ``piece``.
        """
        return self.attacking_pieces.exclude(id=piece.id)


class TerritoryState(PerTurnModel):
    """
    A through model between ``Turn`` and ``Territory``. Represents the state of
    a territory in a given turn.
    """
    territory = models.ForeignKey(
        'Territory',
        null=False,
        related_name='territory_states',
        on_delete=models.CASCADE,
    )
    controlled_by = models.ForeignKey(
        'Nation',
        on_delete=models.CASCADE,
        null=True,
        related_name='controlled_territories',
    )
