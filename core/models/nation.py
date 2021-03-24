import json

from django.contrib.auth.models import User
from django.db import models

from core.models.base import PerTurnModel, Phase, SurrenderStatus


class Nation(models.Model):
    """
    Represents a playable nation in the game, e.g. 'France'.
    """
    id = models.CharField(
        max_length=100,
        null=False,
        primary_key=True,
        editable=False,
    )
    name = models.CharField(
        max_length=15,
    )
    variant = models.ForeignKey(
        'Variant',
        null=False,
        related_name='nations',
        on_delete=models.CASCADE,
    )
    flag = models.TextField()

    class Meta:
        unique_together = ('name', 'variant')

    def __str__(self):
        return self.name

    @property
    def flag_as_data(self):
        if self.flag:
            return json.loads(self.flag)
        return {}


class NationStateQuerySet(models.QuerySet):

    def exclude_civil_disorder(self):
        """
        A NationState instance is considered in civil_disorder if it does not
        have a user controlling it or the user is surrendering.
        """
        qs = self
        return (
            qs
            .filter(user__isnull=False)
            .exclude(surrenders__status=SurrenderStatus.PENDING)
        )


class NationStateManager(models.Manager.from_queryset(NationStateQuerySet)):
    pass


class NationState(PerTurnModel):
    """
    Through model between `Turn`, `User`, and `Nation`. Represents the
    state of a nation during a turn.
    """
    nation = models.ForeignKey(
        'Nation',
        null=False,
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
    # TODO As well as supply delta we should get num_orders to give.

    objects = NationStateManager()
    # TODO add orders finalized at

    # TODO add unique together for turn and nation

    def __str__(self):
        return ' - '.join([str(self.turn), str(self.nation)])

    def copy_to_new_turn(self, turn):
        """
        Create a copy of the instance for the next turn. Created when the turn
        ends and a new turn is created.
        """
        # Set user to None if pending surrender at end of turn
        if self.user_surrendering:
            self.user = None
        self.turn = turn
        self.orders_finalized = False
        self.pk = None
        self.save()
        return self

    @property
    def civil_disorder(self):
        """
        Whether any user can control the nation. Special rules take effect when
        a nation is in civil disorder.

        Returns:
            * `bool`
        """
        return (not self.user) or self.user_surrendering

    @property
    def user_surrendering(self):
        """
        Whether the user that is currently in control of the nation state has
        decided to surrender.

        Returns:
            * `bool`
        """
        return self.surrenders.filter(
            status=SurrenderStatus.PENDING
        ).exists()

    @property
    def meets_victory_conditions(self):
        """
        Determines whether a nation meets the victory conditions of the game
        variant, i.e. controls enough supply centers.

        Returns:
            * `bool`
        """
        num_required = self.turn.game.variant.num_supply_centers_to_win
        return self.supply_centers.count() >= num_required

    @property
    def orders(self):
        """
        Gets the orders that the nation has submitted this turn.

        Returns:
            * `QuerySet`
        """
        return self.nation.orders.filter(turn=self.turn)

    @property
    def pieces(self):
        """
        Gets the pieces that the nation has this turn.

        Returns:
            * QuerySet of `PieceState` instances.
        """
        return self.turn.piecestates.filter(
            piece__nation=self.nation,
        )

    @property
    def supply_centers(self):
        """
        Gets the territories with supply centers that the nation controls this
        turn.

        Returns:
            * Queryset of `TerritoryState` instances
        """
        return self.nation.controlled_territories.filter(
            turn=self.turn,
            territory__supply_center=True
        )

    @property
    def unoccupied_controlled_home_supply_centers(self):
        """
        Get supply centers inside national borders that are under the control
        of the nation and are not occupied. Used by serializers to determine
        where a user nation build.

        Returns:
            * Queryset of `TerritoryState` instances
        """
        return self.nation.controlled_territories.filter(
            turn=self.turn,
            territory__nationality=self.nation,
            territory__supply_center=True,
        ).exclude(
            territory__pieces__turn=self.turn,
        )

    @property
    def supply_delta(self):
        """
        Gets the difference between the number of supply centers a nation
        controls and the number of pieces it has.

        Returns:
            * `int`
        """
        return self.supply_centers.count() - self.pieces.count()

    @property
    def num_builds(self):
        """
        Gets the number of builds that a nation can issue during a build phase.

        Returns:
            * `int`
        """
        num = min(
            self.supply_delta,
            self.unoccupied_controlled_home_supply_centers.count()
        )
        return max(0, num)

    @property
    def num_disbands(self):
        """
        Gets the number of disbands that a nation can issue during a build
        phase.

        Returns:
            * `int`
        """
        num = min(0, self.supply_delta)
        return abs(num)

    @property
    def pieces_to_order(self):
        """
        Get all pieces which a nation can order this turn.

        Returns:
            * Queryset of `PieceState` instances.
        """
        # Can only order pieces which must retreat during retreat phase
        if self.turn.phase == Phase.RETREAT_AND_DISBAND:
            return self.turn.piecestates.filter(
                piece__nation=self.nation,
                must_retreat=True,
            )
        if self.turn.phase == Phase.BUILD:
            raise Exception('Should not be called during build phase')
        return self.turn.piecestates.filter(piece__nation=self.nation)

    @property
    def num_orders(self):
        if self.turn.phase == Phase.BUILD:
            return max(self.num_builds, self.num_disbands)
        return self.pieces_to_order.count()

    @property
    def num_orders_remaining(self):
        if self.turn.phase == Phase.BUILD:
            num_orders = max(self.num_builds, self.num_disbands)
            return max(0, num_orders - self.orders.count())
        return self.pieces_to_order.count() - self.orders.count()


def get_combined_strength(nation_states):
    return sum([ns.supply_centers.count() for ns in nation_states])
