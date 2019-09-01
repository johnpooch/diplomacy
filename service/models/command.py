from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from service.models.base import HygenicModel
from service.models.models import Challenge
from service.models.piece import Piece


class Command(HygenicModel):
    """
    """

    source_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=False
    )
    source_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='+',
        db_column="order_id",
        null=False
    )
    valid = models.BooleanField(default=True)
    success = models.BooleanField(default=True)
    # Outcome in human friendly terms
    result_message = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def clean(self):
        """
        """
        pass

    @property
    def piece(self):
        """
        Helper to get ``source_territory.piece``.
        """
        return self.source_territory.piece

    @property
    def nation(self):
        """
        Helper to get the nation of a command more easily.
        """
        return self.order.nation

    def process(self):
        """
        """
        pass


class TargetCommand(models.Model):
    """
    """
    target_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=False,
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        # check friendly piece exists in source
        if not self.source_territory.friendly_piece_exists(self.nation):
            raise ValidationError(_(
                f'No friendly piece exists in {self.source_territory}.'
            ))


class AuxCommand(TargetCommand):
    """
    """
    aux_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=False,
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        # check piece exists in aux territory
        if not self.aux_territory.occupied():
            raise ValidationError(_(
                f'No piece exists in {self.aux_territory}.'
            ))

        # check aux piece can reach target territory
        if not self.aux_piece.can_reach(self.target_territory):
            raise ValidationError(_(
                f'{self.aux_piece.type.title()} {self.aux_territory} cannot '
                f'reach {self.target_territory}.'
            ))

    @property
    def aux_piece(self):
        return self.aux_territory.piece


class Hold(Command):

    def clean(self):
        """
        """
        # check friendly piece exists in source
        if not self.source_territory.friendly_piece_exists(self.nation):
            raise ValidationError(_(
                f'No friendly piece exists in {self.source_territory}.'
            ))
        return True


class Build(Command):

    piece_type = models.CharField(
        max_length=50,
        null=False,
        choices=Piece.PieceType.CHOICES,
    )

    def clean(self):

        # check territory is not occupied
        if self.source_territory.occupied():
            raise ValidationError(_(
                'Cannot build in occupied territory.'
            ))
        # check source territory has supply center
        if not self.source_territory.has_supply_center():
            raise ValidationError(_(
                'Cannot build in a territory that does not have a supply '
                'center.'
            ))
        # check source territory nationality
        if not self.source_territory.supply_center.nationality == self.nation:
            raise ValidationError(_(
                'Cannot build in supply centers outside of home territory.'
            ))
        # check source territory nationality
        if not self.source_territory.controlled_by == self.nation:
            raise ValidationError(_(
                'Cannot build in supply centers which are not controlled by '
                'nation.'
            ))
        # cannot build fleet inland
        if self.source_territory.is_inland() and \
                self.piece_type == Piece.PieceType.FLEET:
            raise ValidationError(_(
                'Cannot build fleet in inland territory.'
            ))
        return True


class Disband(Command):

    def clean(self):
        # check friendly piece exists in source
        if not self.source_territory.friendly_piece_exists(self.nation):
            raise ValidationError(_(
                f'No friendly piece exists in {self.source_territory}.'
            ))
        return True


class Move(TargetCommand, Command):
    """
    """

    class Meta:
        db_table = 'move'

    target_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True
    )

    def clean(self):
        """
        """

        super().clean()

        # check fleet moving to complex territory specifies named coast
        if self.target_territory.is_complex() \
                and self.source_territory.piece.is_fleet() \
                and not self.target_coast:
            raise ValidationError(_(
                'Cannot order an fleet into a complex territory without '
                'specifying a named coast.'
            ))

        # check piece can reach target territory and target coast
        if not self.piece.can_reach(self.target_territory, self.target_coast):
            raise ValidationError(_(
                f'{self.piece.type.title()} {self.source_territory} cannot reach '
                f'{self.target_territory} {self.target_coast}.'
            ))
        return True

    def process(self):
        """
        """
        Challenge.objects.create(
            piece=self.source_territory.piece,
            territory=self.target_territory
        )


class Support(AuxCommand, Command):
    """
    """

    class Meta:
        db_table = 'support'

    def clean(self):
        """
        """
        super().clean()

        # check piece can reach target territory and target coast
        if not self.piece.can_reach(self.target_territory):
            raise ValidationError(_(
                f'{self.piece.type.title()} {self.source_territory} cannot '
                f'reach {self.target_territory}.'
            ))

        return True

    def process(self):
        """
        """
        pass


class Convoy(AuxCommand, Command):
    """
    """

    class Meta:
        db_table = 'convoy'

    def clean(self):
        """
        """
        super().clean()

        # check that source is sea
        if not self.source_territory.is_sea():
            raise ValidationError(_(
                'Cannot convoy unless piece is at sea.'
            ))

        return True


class Retreat(TargetCommand, Command):
    """
    """

    class Meta:
        db_table = 'retreat'

    target_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True
    )

    def clean(self):
        """
        """
        # TODO test and refactor

        super().clean()

        # check fleet moving to complex territory specifies named coast
        if self.target_territory.is_complex() \
                and self.source_territory.piece.is_fleet() \
                and not self.target_coast:
            raise ValidationError(_(
                'Cannot order an fleet into a complex territory without '
                'specifying a named coast.'
            ))

        # check piece can reach target territory and target coast
        if not self.piece.can_reach(self.target_territory, self.target_coast):
            raise ValidationError(_(
                f'{self.piece.type.title()} {self.source_territory} cannot reach '
                f'{self.target_territory} {self.target_coast}.'
            ))

        # check piece has been dislodged
        if not self.piece.dislodged():
            raise ValidationError(_(
                'Only pieces which have been dislodged can retreat.'
            ))
        # check territory not occupied
        if self.target_territory.occupied():
            raise ValidationError(_(
                'Dislodged piece cannot move to occupied territory.'
            ))
        # check territory not where attacker came from
        if self.target_territory == self.piece.dislodged_by\
                .get_previous_territory():
            raise ValidationError(_(
                'Dislodged piece cannot move to territory from which '
                'attacking piece came.'
            ))
        # check territory not left vacant by standoff on previous turn
        if self.target_territory.standoff_occured_on_previous_turn():
            raise ValidationError(_(
                'Dislodged piece cannot move to territory where a standoff '
                'occured on the previous turn.'
            ))

        return True

    def process(self):
        """
        """
        Challenge.objects.create(
            piece=self.source_territory.piece,
            territory=self.target_territory
        )
