from . import decisions, check
from .decisions import Outcomes
from .decisions.attack_strength import AttackStrength
from .decisions_temp import resolve_convoy_swap


class Order:

    def __init__(self, _id, nation, source):
        self.id = _id
        self.nation = nation
        self.source = source
        self.piece = None
        self.hold_support_orders = set()

        self.outcome = Outcomes.UNRESOLVED
        self.outcome_verbose = None

        self.illegal = False
        self.illegal_code = None
        self.illegal_verbose = None

    def __str__(self):
        piece_type = self.piece.__class__.__name__.lower()
        order_type = self.__class__.__name__.upper()
        aux = getattr(self, 'aux', '')
        aux = f'{aux} ' if aux else ''
        result = f'{self.nation} - {piece_type} {self.source} {order_type} '
        target = getattr(self, 'target', None)
        if target:
            result += f'{aux}-> {self.target}'
        return result

    def __getattr__(self, name):
        """
        Adds the ability to determine the type of an order using the syntax
        `order.is_<order_subclass>`.
        """
        subclasses = Order.__subclasses__()
        for s in subclasses:
            if name == 'is_' + s.__name__.lower():
                return isinstance(self, s)
        raise AttributeError(
            f'{self.__class__.__name__} has no attribute \'{name}\'.'
        )

    @property
    def legal(self):
        return not self.illegal

    def resolve(self):
        if not self.outcome == Outcomes.UNRESOLVED:
            raise ValueError(
                'This order\'s outcome has already been resolved.'
            )
        if self.check_fails():
            self.outcome = Outcomes.FAILS
        elif self.check_succeeds():
            self.outcome = Outcomes.SUCCEEDS

    def set_illegal(self, code, message):
        self.illegal_code = code
        self.illegal_verbose = message
        self.illegal = True
        self.outcome = Outcomes.FAILS

    def check_legal(self):
        """
        Iterate through each legality check. If a check's fail_condition is
        satisfied, set the order to be illegal and set the illegal message.
        """
        for c in self.checks:
            if c().fail_condition(self):
                self.set_illegal(c.code, c.message)
                return

    def to_dict(self):
        return {
            'id': self.id,
            'illegal': self.illegal,
            'illegal_code': self.illegal_code,
            'illegal_verbose': self.illegal_verbose,
            'outcome': self.outcome,
        }


class Hold(Order):

    checks = [
        check.SourcePieceBelongsToNation,
    ]


class Move(Order):

    checks = [
        check.SourcePieceBelongsToNation,
        check.SourceAndTargetDistinct,
        check.ArmyMovesToAdjacentTerritoryNotConvoy,
        check.FleetMovesToAdjacentTerritory,
        check.ArmyCanReachTarget,
        check.FleetCanReachTarget,
        check.FleetCanReachTargetCoastal,
    ]

    def __init__(self, _id, nation, source, target, target_coast=None, via_convoy=False):
        super().__init__(_id, nation, source)
        self.target = target
        self.target_coast = target_coast
        self.via_convoy = via_convoy
        self.move_support_orders = set()
        self.convoy_chains = []

        self.attack_strength_decision = decisions.AttackStrength(self)
        self.prevent_strength_decision = decisions.PreventStrength(self)
        self.defend_strength_decision = decisions.DefendStrength(self)
        self.path_decision = decisions.Path(self)

    def check_succeeds(self):
        min_attack_strength, _ = AttackStrength(self)()
        _, max_to_beat = self._get_strength_to_beat()
        max_prevent = max([p.order.prevent_strength_decision()[1] for p in self.target.other_attacking_pieces(self.piece)], default=0)

        return min_attack_strength > max([max_to_beat, max_prevent])

    def check_fails(self):
        _, max_attack_strength = AttackStrength(self)()
        min_to_beat, _ = self._get_strength_to_beat()
        min_prevent = min([p.order.prevent_strength_decision()[0] for p in self.target.other_attacking_pieces(self.piece)], default=100)

        other_attacking_pieces = self.target.other_attacking_pieces(self.piece)

        if self.path_decision() == Outcomes.NO_PATH:
            self.outcome_verbose = 'Order cannot reach target - {}' \
                .format(self.path_decision.message)
            return True

        lte_min_to_beat = max_attack_strength <= min_to_beat
        lte_min_prevent = other_attacking_pieces \
            and max_attack_strength <= min_prevent

        if lte_min_to_beat or lte_min_prevent:
            self.outcome_verbose = 'Order does not have enough strength'
            return True
        return False

    def resolve(self):
        # TODO convoy swaps should be handled separately
        if self.is_convoy_swap():
            return resolve_convoy_swap(self, self.target.piece.order)
        if self.check_fails():
            self.outcome = Outcomes.FAILS
        elif self.check_succeeds():
            self.outcome = Outcomes.SUCCEEDS

    def move_support(self, *args):
        return [s for s in self.move_support_orders if
                s.outcome in args and s.legal]

    def is_head_to_head(self):
        """
        Determine whether the move is a head to head battle, i.e. the target
        piece is trying to move to this territory.

        Returns:
            * `bool`
        """
        opposing_piece = self.target.piece
        if opposing_piece:
            if opposing_piece.order.is_move:
                if not (self.via_convoy or opposing_piece.order.via_convoy):
                    if opposing_piece.order.legal:
                        return opposing_piece.order.target == self.source
        return False

    def is_convoy_swap(self):
        """
        Determine whether the move is a convoy swap, i.e. the target
        piece is trying to move to this territory via convoy.

        Returns:
            * `bool`
        """
        opposing_piece = self.target.piece
        if opposing_piece:
            if opposing_piece.order.is_move:
                if opposing_piece.order.via_convoy:
                    if opposing_piece.order.legal:
                        if opposing_piece.order.path_decision() == Outcomes.PATH:
                            return opposing_piece.order.target == self.source
        return False

    def _get_strength_to_beat(self):
        if self.is_head_to_head():
            return self.target.piece.order.defend_strength_decision()
        return self.target.hold_strength


class Support(Order):

    checks = [
        check.SourcePieceBelongsToNation,
        check.SourceAndTargetDistinct,
        check.CanReachTargetWithoutConvoy,
    ]

    def __init__(self, _id, nation, source, aux, target):
        super().__init__(_id, nation, source)
        self.aux = aux
        self.target = target

    def check_succeeds(self):
        if not self.piece.dislodged_decision == Outcomes.SUSTAINS:
            return False
        source_attacking_pieces = self.source.other_attacking_pieces(self.target.piece)
        if not source_attacking_pieces:
            return True
        if self.target.piece and self.aux.piece:
            return all([not p.order.attack_strength_decision.max_strength for p in source_attacking_pieces])

    def check_fails(self):
        if self.piece.dislodged_decision == Outcomes.DISLODGED:
            self.outcome_verbose = 'Support fails because dislodged.'
        aux_order = self.aux.piece.order
        aux_piece_moves = aux_order.is_move and aux_order.legal
        if aux_piece_moves and aux_order.target != self.target:
            self.outcome_verbose = 'Aux piece is does not move to target.'
        if not aux_order.is_move:
            if self.target != self.aux:
                self.outcome_verbose = 'Aux piece does not move.'

        if self.source.attacking_pieces and \
                any([p.order.attack_strength_decision()[0] >= 1
                     for p in self.source.attacking_pieces
                     if p.territory != self.target]
                    ):
            self.outcome_verbose = 'Support is cut by attacking piece.'
        return bool(self.outcome_verbose)


class Convoy(Order):

    checks = [
        check.SourcePieceBelongsToNation,
        check.ConvoyeeIsArmy,
        check.AtSea,
    ]

    def __init__(self, _id, nation, source, aux, target):
        super().__init__(_id, nation, source)
        self.aux = aux
        self.target = target


class Retreat(Order):

    checks = [
        check.SourcePieceBelongsToNation,
        check.TargetNotAttackerTerritory,
        check.TargetNotContested,
        check.CanReachTargetWithoutConvoy,
    ]

    def __init__(self, _id, nation, source, target, target_coast=None):
        super().__init__(_id, nation, source)
        self.target = target
        self.target_coast = target_coast

    def resolve(self):

        piece = self.piece
        other_retreating_pieces = self.target.other_retreating_pieces(piece)

        if other_retreating_pieces:
            self.outcome = Outcomes.FAILS
        else:
            self.outcome = Outcomes.SUCCEEDS


class Build(Order):

    checks = [
        check.SourceNotOccupied,
        check.SourceHasSupplyCenter,
        check.SourceWithinNationalBorders,
        check.SourceIsControlled,
        check.PieceTypeCanExist,
        check.SourceNamedCoastNotSpecified,
    ]

    def __init__(self, _id, nation, source, piece_type, named_coast=None):
        super().__init__(_id, nation, source)
        self.piece_type = piece_type
        self.named_coast = named_coast

    def __str__(self):
        order_type = self.p__class__.__name__.upper()
        return f'{self.nation} - {order_type} {self.piece_type} {self.source}'


class Disband(Order):

    checks = [
        check.SourcePieceBelongsToNation,
    ]

    def __str__(self):
        order_type = self.p__class__.__name__.upper()
        return f'{self.nation} - {order_type} {self.piece_type} {self.source}'
