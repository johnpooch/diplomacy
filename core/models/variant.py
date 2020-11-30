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
    # unlike name, this will never change for a given variant
    identifier = models.CharField(
        null=False,
        max_length=100,
    )
    max_num_players = models.PositiveIntegerField(
        null=False,
        default=7,
    )
    num_supply_centers_to_win = models.PositiveIntegerField(
        null=False,
        default=18,
    )
    max_nations_in_draw = models.PositiveIntegerField(
        null=False,
        default=4,
    )
    starting_year = models.PositiveIntegerField(
        null=False,
        default=1901,
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
