from django.db import models

from core.models.base import PerTurnModel, PieceType, \
    TerritoryType


class Territory(models.Model):
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
    supply_center = models.BooleanField(
       default=False,
    )
    initial_piece_type = models.CharField(
        max_length=50,
        null=False,
        choices=PieceType.CHOICES,
    )

    # TODO add validation so that sea territories can't be controlled.

    def __str__(self):
        return self.name

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
                f'More than one piece exists in {self}. There should never be '
                'more than one piece in a territory except when retreating or '
                'disbanding.'))
        return False

    @property
    def is_coastal(self):
        return self.type == TerritoryType.COASTAL

    @property
    def is_sea(self):
        return self.type == TerritoryType.SEA

    @property
    def is_inland(self):
        return self.type == TerritoryType.INLAND

    @property
    def is_complex(self):
        return self.named_coasts.all().exists()


class TerritoryState(PerTurnModel):
    """
    A through model between `Turn` and `Territory`. Represents the state of
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
