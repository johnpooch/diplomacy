from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from service.models.base import HygenicModel
from service.models.models import Challenge


class Command(HygenicModel):
    """
    """

    source_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='source_commands',
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
        related_name='commands',
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


class TargetCommand(Command):
    """
    """
    target_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='target_commands',
        null=False,
    )
    target_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class Move(TargetCommand):
    """
    """

    class Meta:
        db_table = 'move'

    def clean(self):
        """
        """

        # check friendly piece exists in source
        if not self.source_territory.friendly_piece_exists(self.nation):
            raise ValidationError(_(
                f'No friendly piece exists in {self.source_territory}.'
                )
            )

        # check fleet moving to complex territory specifies named coast
        if self.target_territory.is_complex() \
                and self.source_territory.piece.is_fleet() \
                and not self.target_coast:
            raise ValidationError(_(
                'Cannot order an fleet into a complex territory without '
                'specifying a named coast.'
                )
            )

        # check piece can reach target territory and target coast
        if not self.piece.can_reach(self.target_territory, self.target_coast):
            raise ValidationError(_(
                f'{self.piece.type.title()} {self.source_territory} cannot reach '
                f'{self.target_territory} {self.target_coast}.'
                )
            )
        return True

    def process(self):
        """
        """
        Challenge.objects.create(
            piece=self.source_territory.piece,
            territory=self.target_territory
        )
