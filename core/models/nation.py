from django.contrib.auth.models import User
from django.db import models

from core.models.base import PerTurnModel


class Nation(models.Model):
    """
    Represents a playable nation in the game, e.g. 'France'.
    """
    variant = models.ForeignKey(
        'Variant',
        null=False,
        related_name='nations',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=15,
    )

    class Meta:
        db_table = "nation"

    def has_pieces_which_must_retreat(self):
        return any([piece.must_retreat for piece in self.pieces.all()])

    def __str__(self):
        return self.name


class NationState(PerTurnModel):
    """
    Through model between ``Turn``, ``User``, and ``Nation``. Represents the
    state of a nation in during a turn.
    """
    nation = models.ForeignKey(
        'Nation',
        null=False,
        related_name='+',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        null=True,
        related_name='nation_states',
        on_delete=models.CASCADE,
    )
    orders_finalized = models.BooleanField(
        default=False,
    )
    surrendered = models.BooleanField(
        default=False,
    )
