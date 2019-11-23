from copy import deepcopy

from django.apps import apps
from django.db import models

from core.models.base import OrderState, OrderType, OutcomeType, \
    HygenicModel, PieceType
from core.models.mixins.checks import ChecksMixin
from core.models.mixins.decisions import OrderDecisionsMixin
from core.models.mixins.resolver import ResolverMixin


def debug_order(order):
    print('\n')
    print(order)
    if order.type == OrderType.MOVE:
        print(f'MAX ATTACK STRENGTH: {order.max_attack_strength}')
        print(f'MIN ATTACK STRENGTH: {order.min_attack_strength}')

        print(f'MAX DEFEND STRENGTH: {order.max_defend_strength}')
        print(f'MIN DEFEND STRENGTH: {order.min_defend_strength}')

        print(f'MAX PREVENT STRENGTH: {order.max_prevent_strength}')
        print(f'MIN PREVENT STRENGTH: {order.min_prevent_strength}')

        print(f'TERRITORY MAX HOLD STRENGTH: {order.target.max_hold_strength}')
        print(f'TERRITORY MIN HOLD STRENGTH: {order.target.min_hold_strength}')

        print(
            'SUPPORTING COMMANDS: '
            f'{order.supporting_orders}'
        )
        print(
            'OTHER ATTACKING PIECES: '
            f'{order.target.other_attacking_pieces(order.piece)}'
        )

    if order.illegal:
        print(f'COMMAND ILLEGAL MESSAGE: {order.illegal_message}')
    print(f'COMMAND OUTCOME: {order.state}')


class OrderQuerySet(models.QuerySet):

    @property
    def pieces(self):
        """
        """
        # TODO test
        Piece = apps.get_model('core', 'Piece')
        return Piece.objects.filter(order__in=self)


# NOTE this shouldn't be used for everything, only when processing the
# orders.
class OrderManager(models.Manager):
    """
    """
    def get_queryset(self):
        queryset = OrderQuerySet(self.model, using=self._db)
        return queryset

    def process(self):
        """
        Processes all orders in a game.
        """
        # determine whether any orders are illegal
        # NOTE needs to be updated to do correctgame and turn
        all_orders = list(self.get_queryset())
        for order in all_orders:
            order.check_illegal()

        # resolve convoy orders first
        unresolved_fleet_orders = [c for c in all_orders if c.piece.is_fleet]
        self.__resolve_orders(unresolved_fleet_orders, convoys_only=True)

        # resolve all other orders
        unresolved_orders = [c for c in all_orders if c.unresolved]
        self.__resolve_orders(unresolved_orders)

        # TODO improve
        # check all pieces dislodged decision
        [c.piece.dislodged_decision() for c in all_orders if c.piece.unresolved]

        [c.save() for c in all_orders]

    def __resolve_orders(self, unresolved_orders, convoys_only=False):
        """
        """
        # determine whether any convoys are dislodged. This means resolving
        # move and support orders of all other fleets
        resolved_orders = []
        while True:

            # NOTE I have to do this because changing an attribute on the piece
            # doesn't get reflected when the piece is accessed again from the
            # order. There must be a work around for this.
            [c.refresh_from_db() for c in unresolved_orders]

            for order in unresolved_orders:
                if order.piece.unresolved:
                    order.piece.dislodged_decision()

            for order in unresolved_orders:
                if order.unresolved:
                    order.resolve()

            # print(debug_order(order))

            # get resolved_orders
            [resolved_orders.append(c) for c in unresolved_orders
             if not (c.unresolved or c.piece.unresolved)]

            # filter out resolved orders
            unresolved_orders = [c for c in unresolved_orders if
                                   c.unresolved or c.piece.unresolved]

            # return if there are no more unresolved orders
            if convoys_only:
                if not [c for c in unresolved_orders if c.is_convoy]:
                    return
            else:
                if not unresolved_orders:
                    return

    def get_convoying_orders(self, source, target):
        """
        Get all legal orders which are convoying from ``source`` to
        ``target``.

        Args:
            * ``source`` - ``Territory``
            * ``target`` - ``Territory``

        Returns:
            * ``QuerySet`` of ``Order`` instances.
        """
        qs = super().get_queryset()
        return qs.filter(
            type=OrderType.CONVOY,
            aux=source,
            target=target,
            illegal=False
        )

    def get_convoy_paths(self, source, target):
        """
        Gets a list of all available convoy paths from one territory to
        another.

        Args:
            * ``source`` - ``Territory``
            * ``target`` - ``Territory``

        Returns:
            * A ``list`` where each item in the list is a unique ``tuple`` of
            ``Order`` instances. Each ``tuple`` represents a possible convoy
            path.
        """
        convoy_paths = set()
        orders = self.get_convoying_orders(source, target)
        for order in orders:
            if order.source.adjacent_to(source):
                # if direct convoy
                if order.source.adjacent_to(target):
                    # add single order tuple to `convoy_paths`
                    path = (order,)
                    convoy_paths.add(path)
                else:
                    remaining = self.__all_other_orders(orders, order)
                    paths = self.__build_chain([order], target, remaining)
                    if paths:
                        [convoy_paths.add(p) for p in paths]
        return list(convoy_paths)

    def __build_chain(self, initial_chain, target, orders):
        """
        Recursive method which attempts to build a chain of convoying orders
        to a given ``target``.
        """
        complete_chains = []
        for order in orders:
            # if order neigbouring last node in chain, add order to chain
            if order.source.adjacent_to(initial_chain[-1].source):
                chain = initial_chain + [order]

                # path found - neighbouring piece is adjacent to target
                if order.source.adjacent_to(target):
                    complete_chains.append(tuple(chain))
                    continue

                # path not found - check new node's neighbours (recurse)
                remaining = self.__all_other_orders(orders, order)
                inner_chains = self.__build_chain(chain, target, remaining)

                # if the inner method returns complete chains, add them to
                # outer method's complete chains
                if inner_chains:
                    complete_chains.append(inner_chains[0])

        if complete_chains:
            return complete_chains

    @staticmethod
    def __all_other_orders(orders, order_to_remove):
        """
        Helper method to get a copy of a list containing all orders other
        than the given ``order``.
        """
        remaining_orders = list(deepcopy(orders))
        remaining_orders.remove(order_to_remove)
        return remaining_orders


class Order(HygenicModel, ChecksMixin, OrderDecisionsMixin, ResolverMixin):
    """
    """
    nation_state = models.ForeignKey(
        'NationState',
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
        null=True,
        blank=True,
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
    )

    objects = OrderManager()

    class Meta:
        db_table = 'order'

    def __str__(self):
        return f'{self.source.piece.type} {self.source} {self.type}'

    def clean(self):
        """
        """
        try:
            if self.piece.is_army:
                if self.target_coast:
                    raise ValueError('Army order cannot specify a target coast.')
                if self.type == OrderType.CONVOY:
                    raise ValueError('Army cannot convoy.')
        except AttributeError:
            pass

    def set_illegal(self, message):
        self.illegal = True
        self.illegal_message = message
        self.set_fails()

    # NOTE these two shouldn't save
    def set_succeeds(self, save=True):
        self.state = OrderState.SUCCEEDS
        if save:
            self.save()

    def set_fails(self):
        self.state = OrderState.FAILS
        self.save()

    @property
    def unresolved(self):
        return self.state == OrderState.UNRESOLVED

    @property
    def succeeds(self):
        return self.state == OrderState.SUCCEEDS

    @property
    def fails(self):
        return self.state == OrderState.FAILS

    @property
    def successful_support(self):
        return [c for c in self.supporting_orders if c.succeeds]

    @property
    def non_failing_support(self):
        return [c for c in self.supporting_orders if not c.fails]

    @property
    def successful_hold_support(self):
        return [c for c in self.hold_support if c.succeeds]

    @property
    def non_failing_hold_support(self):
        return [c for c in self.hold_support if not c.fails]

    @property
    def supporting_orders(self):
        # TODO test
        if self.type == OrderType.MOVE:
            if not self.illegal:
                return Order.objects.filter(
                    aux=self.source,
                    target=self.target,
                    type=OrderType.SUPPORT,
                )
        return Order.objects.filter(
            aux=self.source,
            target=self.source,
            type=OrderType.SUPPORT,
        )

    @property
    def hold_support(self):
        return Order.objects.filter(
            aux=self.source,
            target=self.source,
            type=OrderType.SUPPORT,
        )

    # TODO bin this
    @property
    def successful_supporting_orders(self):
        return self.supporting_orders.filter(illegal=False)

    @property
    def nation(self):
        return self.order.nation

    @property
    def turn(self):
        return self.order.turn

    @property
    def is_hold(self):
        return self.type == OrderType.HOLD

    @property
    def is_move(self):
        return self.type == OrderType.MOVE

    @property
    def is_support(self):
        return self.type == OrderType.SUPPORT

    @property
    def is_convoy(self):
        return self.type == OrderType.CONVOY

    # TODO move this to decisions
    @property
    def move_path(self):
        """
        Determine whether a move order has a path to the target.

        The path of a move order is successful when the origin and
        destination of the move order are adjacent and accessible by the
        moving piece type, or when there is a chain of adjacent fleets from
        origin to destination each with a matching and successful convoy order.
        """
        if self.type != OrderType.MOVE:
            raise ValueError(
                '`move_path` method can only be used on move orders.'
            )
        if self.source.piece.is_fleet:
            # if moving from named coast, ensure target is neighbour of coast
            if self.source.piece.named_coast:
                return self.target in self.source.piece.named_coast.neighbours.all()

            # if moving from one coast to another, check shared coast
            if self.source.coastal and self.target.coastal:
                return self.target in self.source.shared_coasts.all()

        # check adjacent to target and accessible by piece type
        if self.source.adjacent_to(self.target) and \
                self.target.accessible_by_piece_type(self.source.piece):
            return True

        # if not adjacent, check for convoy
        if self.source.piece.is_army:
            if self.source.coastal and self.target.coastal:
                return self.successful_convoy_exists
        return False

    # TODO move this to decisions (becuase relates only to move path)
    @property
    def successful_convoy_exists(self):
        """
        Determine whether a successful convoy exists between ``source`` and
        ``target``.
        """
        convoy_paths = self.__class__.objects\
            .get_convoy_paths(self.source, self.target)
        for path in convoy_paths:
            if not any([c.piece.dislodged for c in path]):
                return True
        return False

    def head_to_head_exists(self):
        """
        Determine whether the piece in the target territory of a move order
        is moving to the source of this order, i.e. two pieces are trying to
        move into eachother's territories.
        """
        if not self.type == OrderType.MOVE:
            raise ValueError(
                'Only move orders can be in head to head battles.'
            )

        if not self.target.occupied():
            return False

        if not self.target.piece.order.is_move:
            return False

        # if the target piece is moving to this space and has path
        if self.target.piece.order.target == self.source:
            if self.target.piece.order.move_path:
                if not self.target.piece.order.via_convoy and not self.via_convoy:
                    return True
        return False

    # move to manager?
    def get_attack_strength_dependencies(self, dependencies=[]):
        """
        """
        # TODO test
        if self not in dependencies:
            dependencies.append(self)
        else:
            return dependencies
        if self.target.piece:
            if self.target.piece.order.unresolved:
                for c in self.target.piece.order.get_attack_strength_dependencies(dependencies):
                    if c not in dependencies:
                        dependencies.append(c)
        return dependencies
