from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from service.models import HygenicModel


class Piece(HygenicModel):
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
    named_coast = models.OneToOneField(
        'NamedCoast',
        on_delete=models.CASCADE,
        blank=True,
        null=True
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

    def clean(self):
        super().clean()
        # TODO move into methods
        if self.is_fleet():
            if self.territory.is_complex() and not self.named_coast:
                raise ValidationError({
                    'territory': _(
                        'Fleet cannot be in complex territory without also '
                        'being in a named coast.'
                    ),
                })
            if self.territory.is_inland():
                raise ValidationError({
                    'territory': _(
                        'Fleet cannot be in an inland territory.'
                    ),
                })

    def is_army(self):
        return self.type == self.PieceType.ARMY

    def is_fleet(self):
        return self.type == self.PieceType.FLEET

    def can_reach(self, target, target_coast=None):
        """
        """
        # if target coast, check that it is accessible
        if target_coast:
            if self.is_army():
                raise ValueError(_(
                    'Army cannot access named coasts. This error should not be '
                    'happening!'
                ))
            if not self.territory in target_coast.neighbours.all():
                return False

        # Check if convoy is possible
        if self.is_army():
            if self.territory.coastal and target.coastal:
                return True

        if self.is_fleet():
            # if fleet moving from one coast to another, check shared coast
            if self.territory.coastal and target.coastal:
                return target in self.territory.shared_coasts.all()
            if self.territory.is_complex():
                if target not in self.named_coast.neighbours.all():
                    return False

        # Check adjacent to target and accessible by piece type
        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)
