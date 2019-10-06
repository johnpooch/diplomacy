from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from core.models import Command
from core.models.base import HygenicModel, CommandType, PieceType


class Piece(HygenicModel):
    """
    """
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
    dislodged_by = models.ForeignKey(
        'Piece',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "piece"

    def __str__(self):
        return f'{self.type.title()} {self.territory} ({self.nation})'

    def clean(self):
        super().clean()
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
        if self.is_army():
            if self.named_coast:
                raise ValidationError({
                    'territory': _(
                        'Army cannot be n a named coast.'
                    )
                })

    def is_army(self):
        return self.type == PieceType.ARMY

    def is_fleet(self):
        return self.type == PieceType.FLEET

    def get_previous_territory(self):
        # TODO do this when phases/logs are properly handled
        return None

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
            if self.territory not in target_coast.neighbours.all():
                return False

        # Check if convoy is possible
        if self.is_army():
            if self.territory.coastal and target.coastal:
                return True

        if self.is_fleet():
            # if fleet moving from one coast to another, check shared coast
            # (unless complex)
            if self.territory.coastal and target.coastal and not \
                    self.territory.is_complex():
                return target in self.territory.shared_coasts.all()
            if self.territory.is_complex():
                if target not in self.named_coast.neighbours.all():
                    return False

        # Check adjacent to target and accessible by piece type
        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)

    @property
    def dislodged(self):
        """
        - A unit can only be dislodged when it stays in its current space. This
          is the case when the unit did not receive a move order, or if the
          unit was ordered to move but failed. If so, the unit is dislodged if
          another unit has a move order attacking the unit and for which the
          move succeeds.
        """
        if self.command.type == CommandType.MOVE:
            # resolve if unresolved
            if self.command.unresolved:
                self.command.resolve()
            # cannot be dislodged if successfully moved
            if self.command.succeeds:
                return False

        attacking_pieces = self.territory.attacking_pieces
        attacking_commands = Command.objects.filter(
            piece__in=attacking_pieces
        )
        for command in attacking_commands:
            # resolve if unresolved
            print(command)
            if self.command.unresolved:
                self.command.resolve()
            if self.command.succeeds:
                return True
        return False

    @property
    def command(self):
        """
        Helper method to get the unit's current command.
        """
        return
