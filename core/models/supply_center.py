from django.db import models

from core.models.piece import Piece


class SupplyCenter(models.Model):
    """
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
        choices=Piece.PieceType.CHOICES,
    )

    class Meta:
        db_table = "supply_center"

    def __str__(self):
        return f'Supply Center - {self.territory.display_name}'
