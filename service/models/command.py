from django.db import models
from django.utils.translation import gettext as _

from service.models.base import HygenicModel


class Command(HygenicModel):
    """
    """

    class CommandType:
        HOLD = 'hold'
        MOVE = 'move'
        SUPPORT = 'support'
        CHOICES = (
            (HOLD, 'Hold'),
            (MOVE, 'Fleet'),
            (SUPPORT, 'Support'),
        )

    source_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='source_commands',
        null=False
    )
    # aux_territory = models.ForeignKey(
    #     'Territory',
    #     on_delete=models.CASCADE,
    #     related_name='aux_commands',
    #     null=True,
    #     blank=True
    # )
    # source_coast = models.ForeignKey(
    #     'NamedCoast',
    #     on_delete=models.CASCADE,
    #     related_name='+',
    #     null=True,
    #     blank=True
    # )
    # target_coast = models.ForeignKey(
    #     'NamedCoast',
    #     on_delete=models.CASCADE,
    #     related_name='+',
    #     null=True,
    #     blank=True
    # )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='commands',
        db_column="order_id",
        null=False
    )
    type = models.CharField(
        max_length=100,
        choices=CommandType.CHOICES,
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

    objects = models.Manager()

    class Meta:
        abstract = True

    def clean(self):
        """
        """
        self.is_valid()

    @property
    def source_piece(self):
        """
        """
        return self.source_territory.piece

    def process(self):
        """
        """
        if self.type == self.CommandType.MOVE:
            Challenge.objects.create(
                piece=self.source_piece,
                territory=self.target_territory
            )


class Move(Command):
    """
    """
    target_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='target_commands',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'move'

    def is_valid(self):
        """
        """
        if not self._friendly_piece_exists_in_source():
            raise ValidationError(_(
                f'No friendly piece exists in {self.source_territory}.'
                )
            )
        if not self.piece.can_reach(self.target_territory):
            raise ValidationError(_(
                f'{self.piece.type} {self.source_territory} cannot reach '
                f'{self.target_territory}.'
                )
            )
        return True
