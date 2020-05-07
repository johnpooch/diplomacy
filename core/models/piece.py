import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from core.models.base import HygienicModel, PerTurnModel, \
    PieceType


class Piece(HygienicModel):

    nation = models.ForeignKey(
        'Nation',
        null=False,
        related_name='pieces',
        on_delete=models.CASCADE,
    )
    game = models.ForeignKey(
        'Game',
        null=False,
        related_name='pieces',
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        max_length=50,
        null=False,
        choices=PieceType.CHOICES,
        default=PieceType.ARMY,
    )

    @property
    def is_army(self):
        return self.type == PieceType.ARMY

    @property
    def is_fleet(self):
        return self.type == PieceType.FLEET


class PieceState(PerTurnModel):
    """
    Represents a piece during a turn.

    At the beginning of every turn a new `PieceState` instance is created for
    each in-game piece.
    """
    piece = models.ForeignKey(
        'Piece',
        null=False,
        on_delete=models.CASCADE,
        related_name='states'
    )
    territory = models.ForeignKey(
        'Territory',
        null=True,
        on_delete=models.CASCADE,
        related_name='pieces',
    )
    named_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='pieces',
    )
    dislodged = models.BooleanField(
        default=False
    )
    dislodged_by = models.OneToOneField(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='piece_disloged',
    )
    attacker_territory = models.ForeignKey(
        'Territory',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text=_(
            'If the piece was dislodged via a land attack, the piece cannot '
            'to the attacking piece\'s territory.'
        )
    )

    def __str__(self):
        # TODO Fix this up and make it used in all the error messages. Also
        # make fixtures use title instead of using `title()`
        return f'{self.piece.type} {str(self.territory)} ({self.piece.nation})'

    def clean(self):
        super().clean()
        if self.piece.is_fleet:
            if self.territory.is_complex and not self.named_coast:
                raise ValidationError({
                    'territory': _(
                        'Fleet cannot be in complex territory without also '
                        'being in a named coast.'
                    ),
                })
            if self.territory.is_inland:
                raise ValidationError({
                    'territory': _(
                        'Fleet cannot be in an inland territory.'
                    ),
                })
        if self.piece.is_army:
            if self.named_coast:
                raise ValidationError({
                    'territory': _(
                        'Army cannot be on a named coast.'
                    )
                })

    def to_dict(self):
        data = {
            '_id': self.pk,
            'type': self.piece.type,
            'nation': self.piece.nation.id,
            'territory_id': self.territory.id,
        }
        if self.attacker_territory:
            data['attacker_territory'] = self.attacker_territory.id
        return data
