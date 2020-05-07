from django.db import models

from .base import Phase, Season


class Variant(models.Model):
    """
    Represents a variant of diplomacy. The main variant of the game is the
    standard variant but there are other variants like 'Versailles'.
    """
    name = models.CharField(
        null=False,
        max_length=100,
    )
    max_num_players = models.PositiveIntegerField(
        null=False,
        default=7,
    )
    starting_year = models.PositiveIntegerField(
        null=False,
        default=1900,
    )
    starting_season = models.CharField(
        null=False,
        default=Season.SPRING,
        choices=Season.CHOICES,
        max_length=100,
    )
    starting_phase = models.CharField(
        null=False,
        default=Phase.ORDER,
        choices=Phase.CHOICES,
        max_length=100,
    )

    def __str__(self):
        return self.name
