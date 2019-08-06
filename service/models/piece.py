from django.db import models

class Piece(models.Model):
    """
    """
    class PieceType:
        ARMY = 'army'
        FLEET = 'fleet'
        CHOICES = (
            (ARMY, 'Army'),
            (FLEET, 'Fleet'),
        )

    nation = models.ForeignKey(
        'Nation',
        related_name='pieces',
        on_delete=models.CASCADE,
        db_column="nation_id",
        null=False,
        db_constraint=False,
    )
    territory = models.OneToOneField(
        'Territory',
        on_delete=models.CASCADE,
        null=True,
    )
    type = models.CharField(
        max_length=50,
        null=False,
        choices=PieceType.CHOICES,
        default=PieceType.ARMY,
    )
    must_retreat = models.BooleanField(default=False)
    must_disband = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "piece"

    def __str__(self):
        return f'{self.type.title()} {self.territory} ({self.nation})'

    def is_army(self):
        return self.type == self.PieceType.ARMY

    def is_fleet(self):
        return self.type == self.PieceType.FLEET
