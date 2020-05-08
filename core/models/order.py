from django.core.exceptions import ValidationError
from django.db import models

from core.models.base import OrderType, OutcomeType, PerTurnModel, PieceType


class Order(PerTurnModel):

    nation = models.ForeignKey(
        'Nation',
        null=False,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    type = models.CharField(
        max_length=8,
        null=False,
        choices=OrderType.CHOICES,
        default=OrderType.HOLD
    )
    source = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=False,
        blank=False,
    )
    target = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True,
    )
    target_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True
    )
    aux = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True,
    )
    # Only used on build orders
    piece_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=PieceType.CHOICES,
    )
    via_convoy = models.BooleanField(
        default=False
    )
    outcome = models.CharField(
        choices=OutcomeType.CHOICES,
        max_length=25,
        null=True,
        blank=True,
    )
    legal = models.BooleanField(
        default=True,
    )
    illegal_message = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )

    def __str__(self):
        string = f'{self.nation} {self.type} {self.source}'
        if self.type in [OrderType.MOVE, OrderType.RETREAT]:
            string += f' - {self.target}'
        if self.type in [OrderType.SUPPORT, OrderType.CONVOY]:
            string += f' - {self.aux} - {self.target}'
        return string

    def clean(self):
        if self.via_convoy and self.type != OrderType.MOVE:
            raise ValidationError({
                'via_convoy': (
                    'Via convoy should only be specified for move orders.'
                ),
            })
        if self.piece_type and self.type != OrderType.BUILD:
            raise ValidationError({
                'piece_type': (
                    'Piece type should only be specified for build orders.'
                ),
            })
        print('HAHFSDFJGSHDFG')
        if self.type not in self.turn.possible_order_types:
            raise ValidationError({
                'type': (
                    'This order type is not possible during this turn.'
                ),
            })

    def to_dict(self):
        data = {
            '_id': self.pk,
            'type': self.type,
            'nation': self.nation.id,
            'source_id': self.source.id,
            'via_convoy': self.via_convoy,
            'piece_type': self.piece_type,
        }
        if self.target:
            data['target_id'] = self.target.id
        if self.aux:
            data['aux_id'] = self.aux.id
        return data
