from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from core.models.base import (
    PerTurnModel, PieceType, Phase, Season, TerritoryType
)


class Territory(models.Model):
    """
    Represents an area in the game map that can be occupied.
    """
    name = models.CharField(
        max_length=50,
        null=False,
    )
    uid = models.CharField(
        max_length=100,
        null=False,
        unique=True,
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
        blank=False,
        null=False
    )
    supply_center = models.BooleanField(
        default=False,
    )
    initial_piece_type = models.CharField(
        max_length=50,
        null=True,
        choices=PieceType.CHOICES,
    )

    class Meta:
        unique_together = ('name', 'variant')
        verbose_name_plural = 'territories'

    def __str__(self):
        return self.name

    def state(self, turn):
        return self.territory_states.get(turn=turn)

    def adjacent_to(self, territory):
        return territory in self.neighbours.all()

    def shares_coast_with(self, territory):
        return territory in self.shared_coasts.all()

    def get_piece(self):
        """
        Return the piece if it exists in the territory. If no piece exists
        in the territory, return `None`. If there is are two pieces in a
        territory, gets the non-retreating piece.

        Returns:
            * `PieceState` or `None` if there is no piece in the territory.
        """
        try:
            return self.pieces.get(must_retreat=False)
        except ObjectDoesNotExist:
            return None

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
    contested = models.BooleanField(
        default=False,
    )
    bounce_occurred = models.BooleanField(
        default=False,
    )

    def copy_to_new_turn(self, turn):
        self.pk = None
        # if end of fall orders process change of possession.
        if (
            self.turn.phase == Phase.ORDER
            and self.turn.season == Season.FALL
            and not self.territory.type == TerritoryType.SEA
        ):
            try:
                occupying_piece = self.turn.piecestates.get(
                    territory=self.territory,
                    must_retreat=False
                )
                self.controlled_by = occupying_piece.piece.nation
            except ObjectDoesNotExist:
                pass

        self.contested = self.bounce_occurred
        self.bounce_occurred = False
        self.turn = turn
        self.save()
        return self
