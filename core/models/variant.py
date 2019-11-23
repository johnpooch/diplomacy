from django.db import models


class Variant(models.Model):
    """
    Represents a variant of diplomacy. The main variant of the game is the
    standard variant but there are other variants like 'Versailles'.
    """
    name = models.CharField(
        null=False,
        max_length=100,
    )
    num_players = models.PositiveIntegerField(
        null=False,
        default=7,
    )
