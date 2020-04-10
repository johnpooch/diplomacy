from django.apps import apps
from django.contrib.auth.models import User
from django.db import models

from core.models.base import PerTurnModel


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
    def orders_remaining(self):
        """
        Gets the number of orders that the nation can still submit.

        Returns:
            * `int`
        """
        return self.num_supply_centers - self.orders.count()
