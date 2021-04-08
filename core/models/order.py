from django.core.exceptions import ValidationError
from django.db import models

from core.models.base import OrderType, OutcomeType, PerTurnModel, Phase, \
    PieceType


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
        related_name='source_orders',
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
    outcome_verbose = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    illegal = models.BooleanField(
        default=False,
    )
    illegal_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    illegal_verbose = models.CharField(
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
        if self.type not in self.turn.possible_order_types:
            raise ValidationError({
                'type': (
                    'This order type is not possible during this turn.'
                ),
            })

    @classmethod
    def validate(cls, nation_state, data):
        turn = nation_state.turn
        territory = data['source']
        if data.get('via_convoy') and data['type'] != OrderType.MOVE:
            raise ValidationError({
                'via_convoy': (
                    'Via convoy should only be specified for move orders.'
                ),
            })
        if data.get('piece_type') and data['type'] != OrderType.BUILD:
            raise ValidationError({
                'piece_type': (
                    'Piece type should only be specified for build orders.'
                ),
            })
        if data['type'] not in turn.possible_order_types:
            raise ValidationError({
                'type': (
                    'This order type is not possible during this turn.'
                ),
            })
        if data['type'] not in turn.possible_order_types:
            raise ValidationError({
                'type': (
                    'This order type is not possible during this turn.',
                )
            })
        if turn.phase == Phase.BUILD:
            if data['type'] == OrderType.BUILD:
                if territory not in \
                        [ts.territory for ts in nation_state.unoccupied_controlled_home_supply_centers]:
                    raise ValidationError({
                        'type': ('Cannot build in this territory.')
                    })
                if not nation_state.num_orders_remaining:
                    raise ValidationError({
                        'type': ('Cannot issue any more build orders.')
                    })
            if data['type'] == OrderType.DISBAND:
                if not nation_state.num_orders_remaining:
                    raise ValidationError({
                        'type': ('Cannot issue any more disband orders.')
                    })
        else:
            pieces_to_order = nation_state.pieces_to_order
            if territory not in [p.territory for p in pieces_to_order]:
                raise ValidationError({
                    'type': ('Cannot create an order for this territory.')
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
        if self.target_coast:
            data['target_coast_id'] = self.target_coast.id
        if self.aux:
            data['aux_id'] = self.aux.id
        return data
