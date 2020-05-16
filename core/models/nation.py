from django.apps import apps
from django.contrib.auth.models import User
from django.db import models

from core.models.base import PerTurnModel, Phase


class Nation(models.Model):
    """
    Represents a playable nation in the game, e.g. 'France'.
    """
    variant = models.ForeignKey(
        'Variant',
        null=False,
        related_name='nations',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=15,
    )

    def __str__(self):
        return self.name


class NationState(PerTurnModel):
    """
    Through model between `Turn`, `User`, and `Nation`. Represents the
    state of a nation in during a turn.
    """
    nation = models.ForeignKey(
        'Nation',
        null=False,
        related_name='+',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        null=True,
        related_name='nation_states',
        on_delete=models.CASCADE,
    )
    orders_finalized = models.BooleanField(
        default=False,
    )
    surrendered = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return ' - '.join([str(self.turn), str(self.nation)])

    @property
    def num_supply_centers(self):
        """
        Gets the number of supply centers that the nation controls this turn.

        Returns:
            * `int`
        """
        TerritoryState = apps.get_model(
            app_label='core',
            model_name='TerritoryState'
        )
        return TerritoryState.objects.filter(
            controlled_by=self.nation,
            territory__supply_center=True,
        ).count()

    @property
    def orders(self):
        """
        Gets the orders that the nation has submitted this turn.

        Returns:
            * `QuerySet`
        """
        Order = apps.get_model(app_label='core', model_name='Order')
        return Order.objects.filter(
            turn=self.turn,
            nation=self.nation,
        )

    @property
    def num_orders(self):
        """
        Gets the number of orders that the nation can submit this turn.

        Returns:
            * `int`
        """
        PieceState = apps.get_model(
            app_label='core',
            model_name='PieceState'
        )
        return PieceState.objects \
            .filter(turn=self.turn, piece__nation=self.nation).count()

    @property
    def pieces_to_order(self):
        """
        Get all pieces which a nation can order this turn.

        Returns:
            * Queryset of `PieceState` instances.
        """
        PieceState = apps.get_model(
            app_label='core',
            model_name='PieceState'
        )
        # Can only order pieces which must retreat during retreat phase
        if self.turn.phase == Phase.RETREAT_AND_DISBAND:
            return PieceState.objects.filter(
                turn=self.turn,
                piece__nation=self.nation,
                must_retreat=True,
            )
        if self.turn.phase == Phase.BUILD:
            raise Exception('Should not be called during build phase')
        return PieceState.objects.filter(
            turn=self.turn,
            piece__nation=self.nation,
        )


    # TODO wrong
    @property
    def orders_remaining(self):
        """
        Gets the number of orders that the nation can still submit.

        Returns:
            * `int`
        """
        return self.num_supply_centers - self.orders.count()
