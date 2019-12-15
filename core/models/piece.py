import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from core.models.base import HygenicModel, PerTurnModel, DislodgedState, \
    PieceType


class Piece(HygenicModel, PerTurnModel):
    """
    Represents a piece during a turn.

    At the beginning of every turn a new ``Piece`` instance is created for each
    in-game piece. ``Piece`` instances representing the same in-game piece are
    related by their ``persisted_piece_id``.
    """
    persisted_piece_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text=_(
            'This ID is persisted across `Piece` instances to which belong to '
            'the same in game piece.'
        )
    )
    nation = models.ForeignKey(
        'Nation',
        null=False,
        related_name='pieces',
        on_delete=models.CASCADE,
    )
    # NOTE should this use TerritoryState?
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
    retreat_territories = models.ManyToManyField(
        'Territory',
        blank=True,
        related_name='retreat_pieces'
    )

    def __str__(self):
        # TODO Fix this up and make it used in all the error messages. Also
        # make fixtures use title instead of using `title()`
        return f'{self.type.title()} {str(self.territory)} ({self.nation})'

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

    @property
    def moves(self):
        return self.command.succeeds and self.command.is_move

    @property
    def stays(self):
        return not self.command.is_move or self.command.fails

    @property
    def dislodged(self):
        return self.dislodged_state == DislodgedState.DISLODGED

    @property
    def sustains(self):
        return self.dislodged_state == DislodgedState.SUSTAINS

    @property
    def unresolved(self):
        return self.dislodged_state == DislodgedState.UNRESOLVED

    # NOTE these should not save
    def set_sustains(self):
        self.dislodged_state = DislodgedState.SUSTAINS
        self.save()

    def set_dislodged(self, piece):
        self.dislodged_state = DislodgedState.DISLODGED
        self.dislodged_by = piece
        self.save()

    def get_previous_territory(self):
        # TODO do this when phases/logs are properly handled
        # NOTE maybe just denormalize into a field
        return None

    def can_reach(self, target, target_coast=None):
        """
        """
        # if target coast, check that it is accessible
        if target_coast:
            if self.is_army:
                raise ValueError(_(
                    'Army cannot access named coasts. This error should not be '
                    'happening!'
                ))
            return self.territory in target_coast.neighbours.all()

        # Check if convoy is possible
        if self.is_army:
            if self.territory.coastal and target.coastal:
                return True

        if self.is_fleet:
            # if fleet moving from one coast to another, check shared coast
            # (unless complex)
            if self.territory.coastal and target.coastal and not \
                    self.territory.is_complex:
                return target in self.territory.shared_coasts.all()
            if self.territory.is_complex:
                if target not in self.named_coast.neighbours.all():
                    return False

        # Check adjacent to target and accessible by piece type
        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)

    # TODO move to decisions
    def dislodged_decision(self):
        """
        """
        if not self.dislodged_state == DislodgedState.UNRESOLVED:
            raise ValueError(
                'Cannot call `dislodged_decision()` on a piece for which '
                '`dislodged_state` has already been determined.'
            )
        attacking_pieces = list(self.territory.attacking_pieces)

        # sustains if...
        if not attacking_pieces:
            return self.set_sustains()
        if self.command.is_move:
            # cannot be dislodged if successfully moved
            if self.command.succeeds:
                return self.set_sustains()
        if [p for p in attacking_pieces
                if p.command.fails] and all([p.command.fails for p in attacking_pieces]):
            return self.set_sustains()

        # dislodged if...
        if self.command.is_move:
            if self.command.fails and any([p for p in attacking_pieces
                                           if p.command.succeeds]):
                piece = [p for p in attacking_pieces if
                         p.command.succeeds][0]
                return self.set_dislodged(piece)
        else:
            if any([p.command.succeeds for p in attacking_pieces]):
                piece = [p for p in attacking_pieces
                         if p.command.succeeds][0]
                return self.set_dislodged(piece)
