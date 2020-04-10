import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from core.models.base import HygienicModel, PerTurnModel, \
    PieceType


class Piece(HygienicModel, PerTurnModel):
    """
    Represents a piece during a turn.

    At the beginning of every turn a new `Piece` instance is created for each
    in-game piece. `Piece` instances representing the same in-game piece are
    related by their `persisted_piece_id`.
    """
    persisted_piece_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text=_(
            'This ID is persisted across `Piece` instances which belong to '
            'the same in game piece.'
        )
    )
    nation = models.ForeignKey(
        'Nation',
        null=False,
        related_name='pieces',
        on_delete=models.CASCADE,
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
    type = models.CharField(
        max_length=50,
        null=False,
        choices=PieceType.CHOICES,
        default=PieceType.ARMY,
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
        return f'{self.type} {str(self.territory)} ({self.nation})'

    def clean(self):
        super().clean()
        if self.is_fleet:
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
        if self.is_army:
            if self.named_coast:
                raise ValidationError({
                    'territory': _(
                        'Army cannot be on a named coast.'
                    )
                })

    @property
    def is_army(self):
        return self.type == PieceType.ARMY

    @property
    def is_fleet(self):
        return self.type == PieceType.FLEET

    def get_previous_territory(self):
        # TODO do this when phases/logs are properly handled
        # NOTE maybe just denormalize into a field
        return None

    def to_dict(self):
        data = {
            '_id': self.pk,
            'type': self.type,
            'nation': self.nation.id,
            'territory_id': self.territory.id,
        }
        if self.attacker_territory:
            data['attacker_territory'] = self.attacker_territory.id
        return data
