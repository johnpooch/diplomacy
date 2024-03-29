from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from core.models.base import (
    HygienicModel, OrderType, OutcomeType, PerTurnModel, PieceType
)


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
    # TODO both of these fields should be replaced with properties
    turn_created = models.ForeignKey(
        'Turn',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+',
        help_text=_(
            'The turn during which this piece was created. Will always '
            'be a build phase. If null, piece was created at the beginning '
            'of the game.'
        )
    )
    turn_disbanded = models.ForeignKey(
        'Turn',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+',
        help_text=_(
            'The turn during which this piece was disbanded. Will always '
            'be a retreat/disband phase or a build/disband phase.'
        )
    )
    turn_destroyed = models.ForeignKey(
        'Turn',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+',
        help_text=_(
            'The turn during which this piece was destroyed.'
        )
    )

    def __str__(self):
        return f'{self.type} ({self.nation}) {self.id}'

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
        related_name='piece_dislodged',
    )
    dislodged_from = models.ForeignKey(
        'Territory',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text=_(
            'True if the piece was dislodged via a land attack during this '
            'turn. The piece\'s attacker_territory field will be set to this '
            'value next turn.'
        ),
        related_name='pieces_dislodged_from_here',
    )
    destroyed = models.BooleanField(
        default=False
    )
    destroyed_message = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    must_retreat = models.BooleanField(
        default=False,
        help_text=_(
            'Signifies that the piece was dislodged in the previous turn and '
            'now must retreat.'
        )
    )
    attacker_territory = models.ForeignKey(
        'Territory',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text=_(
            'True if the piece was dislodged via a land attack in the '
            'previous turn. During this turn the piece cannot to the '
            'attacking piece\'s territory.'
        )
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['turn', 'territory', 'must_retreat'],
                name='unique_piece_in_territory,'
            )
        ]

    def __str__(self):
        # TODO Fix this up and make it used in all the error messages. Also
        # make fixtures use title instead of using `title()`
        return f'{self.piece.type} {str(self.territory)} ({self.piece.nation})'

    @property
    def successful_move_order(self):
        """
        Get the successful move or retreat order for a piece state if one
        exists.
        """
        return self.territory.source_orders.filter(
            nation=self.piece.nation,
            outcome=OutcomeType.SUCCEEDS,
            type__in=[OrderType.MOVE, OrderType.RETREAT],
            turn=self.turn,
        ).first()

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

    def copy_to_new_turn(self, turn):
        """
        Create a copy of the instance for the next turn. Created when the turn
        ends and a new turn is created.

        Args:
            * `turn` - `Turn` - The new turn instance that the piece is being
              copied to.
        """
        # If piece disbanded or destroyed do not create a new piece state
        if self.piece.turn_disbanded or self.destroyed:
            return None
        piece_data = {
            'piece': self.piece,
            'territory': self.territory,
            'named_coast': self.named_coast,
            'must_retreat': False,
        }
        move_order = self.successful_move_order
        if move_order:
            piece_data['territory'] = move_order.target
            piece_data['named_coast'] = move_order.target_coast

        # if piece dislodged set next piece to must_retreat. Record where the
        # piece was attacked from. The piece will not be able to retreat to
        # that territory next turn.
        if self.dislodged:
            piece_data['must_retreat'] = True
            piece_data['attacker_territory'] = self.dislodged_from
        return turn.piecestates.create(**piece_data)

    # TODO test
    def restore_to_turn(self, turn):
        self.pk = None
        self.turn = turn
        self.dislodged = False
        self.dislodged_by = None
        self.dislodged_from = None
        self.destroyed = False
        self.destroyed_message = None
        self.save()
        return self
