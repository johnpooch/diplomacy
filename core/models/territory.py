from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from core.models import Piece
from core.models.base import CommandType, PieceType


class Territory(models.Model):
    """
    """
    class TerritoryType:
        LAND = 'land'
        SEA = 'sea'
        CHOICES = (
            (LAND, 'Land'),
            (SEA, 'Sea'),
        )
    # TODO add ForeignKey to Variant. Create Variant model.
    # TODO territory should inherit from a model called space which has details
    # about the representation of the territory on the front end.
    # TODO there should be an ImpassableTerritory model which inherits from
    # Space too.
    name = models.CharField(max_length=50, null=False, unique=True)
    controlled_by = models.ForeignKey(
        'Nation',
        on_delete=models.CASCADE,
        null=True,
        related_name='controlled_territories',
    )
    # TODO nationality and controlled by should be synced up on game
    # initializaition.
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
    coastal = models.BooleanField(default=False)

    class Meta:
        db_table = "territory"

    # TODO add validation so that sea territories can't be controlled.

    def __str__(self):
        return self.name.title()

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
            return self.type == self.TerritoryType.LAND
        return (self.type == self.TerritoryType.SEA) or self.coastal

    def has_supply_center(self):
        try:
            return bool(self.supply_center)
        except ObjectDoesNotExist:
            return False

    def is_land(self):
        return self.type == self.TerritoryType.LAND and not self.coastal

    def is_sea(self):
        return self.type == self.TerritoryType.SEA

    def is_inland(self):
        return self.is_land() and not self.coastal

    def is_complex(self):
        return self.named_coasts.all().exists()

    @property
    def attacking_pieces(self):
        """
        Helper method to get all pieces which are moving into this territory.
        """
        return Piece.objects.filter(
            command__target=self,
            command__type=CommandType.MOVE
        )

    @property
    def max_hold_strength(self):
        """
        Determine the maximum 'hold_strength' of a territory. It should
        always be possible to determine this.
        """
        # TODO test
        if not self.occupied():
            return 0
        if self.piece.command.type == CommandType.MOVE:
            if not self.piece.command.unresolved:
                if self.piece.command.succeeds:
                    return 0
                if self.piece.command.fails:
                    return 1
        # return 1 plus the number of supporting pieces that are successful or
        # unresolved
        return 1 + len([c for c in self.piece.command.supporting_commands
                        if not c.fails])

    @property
    def min_hold_strength(self):
        """
        Determine the minimum 'hold_strength' of a territory. It should always be
        possible to determine this.
        """
        # TODO test
        if not self.occupied():
            return 0
        if self.piece.command.type == CommandType.MOVE:
            if not self.piece.command.fails:
                return 0
            else:
                return 1
        # return 1 plus the number of supporting pieces that are successful
        return 1 + len([c for c in self.piece.command.supporting_commands
                        if c.succeeds])

    # @property
    # def hold_strength(self):
    #     # TODO test
    #     """
    #     Unlike ``attack_strength``,  ``hold_strength`` is defined for a
    #     territory, rather than for a command.

    #     Returns 0 when the territory is empty, or when it contains a unit that
    #     is ordered to move and for which the move succeeds.

    #     Returns 1 when the area contains a unit that is ordered to move and for
    #     which the move fails.

    #     In all other cases, returns 1 plus the number of orders that
    #     successfully support the unit to hold.
    #     """
    #     if not self.occupied():
    #         return 0

    #     # maybe change this to make it return a range (lowest possible, highest_possible)
    #     # also maybe explore head to head
    #     if self.piece.command.type == CommandType.MOVE:
    #         # resolve if unresolved
    #         if self.piece.command.source == self.piece.command.target:
    #             return 0
    #         if self.piece.command.unresolved:
    #             self.piece.command.resolve()
    #         if self.piece.command.succeeds:
    #             return 0
    #         if self.piece.command.fails:
    #             return 1

    #     return 1 + len([c for c in self.piece.command.supporting_commands
    #                     if c.succeeds])


    #     if not self.occupied() or \
    #             (self.piece.command.state == CommandState.resolved and
    #              self.target.piece.command.type == 'MOVE'):
    #         return 1 + self.support

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
