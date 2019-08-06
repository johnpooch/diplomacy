from django.core.exceptions import ObjectDoesNotExist
from django.db import models


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
    # TODO there should be an ImpassableTerritory model which inherits from Space too.
    name = models.CharField(max_length=50, null=False)
    controlled_by = models.ForeignKey(
        'Nation',
        on_delete=models.CASCADE,
        null=True,
        related_name='controlled_territories',
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

    def is_neighbour(self, territory):
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
            raise ValueError((f"More than one piece exists in {self}. "
                    "There should never be more than one piece in a territory "
                    "except when retreating or disbanding."))
        return False

    def get_friendly_piece(self, nation):
        """
        Get piece belonging to nation if exists in territory.
        """
        for piece in self.pieces.all():
            if piece.nation == nation:
                return piece
        return False

    def accessible_by_piece_type(self, piece):
        """
        Armies cannot enter sea territories. Fleets cannot enter non-coastal
        land territories.
        """
        if piece.type == piece.PieceType.ARMY:
            return self.type == self.TerritoryType.LAND
        return (self.type == self.TerritoryType.SEA) or self.coastal

    def has_supply_center(self):
        try:
            return bool(self.supply_center)
        except ObjectDoesNotExist:
            return False

    def __str__(self):
        return self.name.capitalize()