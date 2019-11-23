from django.db import models

from core.models.base import PieceType


class SupplyCenter(models.Model):
    """
    Represents a supply center on the game map.

    The state of the supply center is the same as the state of the related
    ``Territory`` so a ``SupplyCenterState`` model is not necessary.
    """
    nationality = models.ForeignKey(
        'Nation',
        related_name='national_supply_centers',
        on_delete=models.CASCADE,
        null=True
    )
    territory = models.OneToOneField(
        'Territory',
        primary_key=True,
        on_delete=models.CASCADE,
        db_column='territory_id',
        related_name='supply_center',
        null=False
    )
    initial_piece_type = models.CharField(
        max_length=50,
        null=False,
        choices=PieceType.CHOICES,
    )

    class Meta:
        db_table = "supply_center"

    def __str__(self):
        return f'Supply Center - {self.territory.display_name}'


class SupplyCenterState(models.Model):
    """
    """
    # TODO state or per turn attribute
    turn = models.ForeignKey(
        'Turn',
        related_name='supply_center_states',
        on_delete=models.CASCADE,
        null=False,
    )
    supply_center = models.ForeignKey(
        'SupplyCenter',
        related_name='states',
        on_delete=models.CASCADE,
        null=False,
    )
    controlled_by = models.ForeignKey(
        'Nation',
        related_name='supply_center_states',
        on_delete=models.CASCADE,
        null=False,
    )
