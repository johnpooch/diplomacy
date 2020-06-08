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

    def set_outcome(self, outcome):
        self.outcome = outcome
        return self.outcome

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
        if self.piece:
            if self.piece.dislodged_decision == Outcomes.DISLODGED:
                outcome = Outcomes.FAILS
            else:
                outcome = Outcomes.SUCCEEDS
        return {
            'id': self.id,
            'legal': self.legal,
            'illegal_verbose': self.illegal_verbose,
            'outcome': outcome,
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

    def update_move_decision(self):

        if self.path_decision() == Outcomes.NO_PATH:
            return self.set_outcome(Outcomes.FAILS)

        if self.path_decision() == Outcomes.UNRESOLVED:
            return

        if self.is_head_to_head():
            return self._resolve_head_to_head()

        if self.is_convoy_swap():
            return resolve_convoy_swap(self, self.target.piece.order)

        piece = self.piece
        min_attack_strength, max_attack_strength = AttackStrength(self)()

        target_min_hold = self.target.hold_strength[0]
        target_max_hold = self.target.hold_strength[1]

        other_attacking_pieces = self.target.other_attacking_pieces(piece)
        other_pieces_max_prevent = max([p.order.prevent_strength_decision()[1] for p in other_attacking_pieces], default=0)
        other_pieces_min_prevent = min([p.order.prevent_strength_decision()[0] for p in other_attacking_pieces], default=0)

        # succeeds if...
        if other_attacking_pieces:
            if min_attack_strength > target_max_hold:
                if min_attack_strength > other_pieces_max_prevent:
                    return self.set_outcome(Outcomes.SUCCEEDS)
        else:
            if min_attack_strength > target_max_hold:
                return self.set_outcome(Outcomes.SUCCEEDS)

        # fails if...
        if max_attack_strength <= target_min_hold:
            return self.set_outcome(Outcomes.FAILS)

        if other_attacking_pieces:
            if max_attack_strength <= other_pieces_min_prevent:
                return self.set_outcome(Outcomes.FAILS)

    def _resolve_head_to_head(self):

        piece = self.piece
        opposing_unit = self.target.piece
        opposing_min_defend, opposing_max_defend = opposing_unit.order.defend_strength_decision()
        min_attack_strength, max_attack_strength = AttackStrength(self)()
        other_attacking_pieces = self.target.other_attacking_pieces(piece)
        other_pieces_min_prevent = max([p.order.prevent_strength_decision()[0] for p in other_attacking_pieces], default=0)
        other_pieces_max_prevent = max([p.order.prevent_strength_decision()[1] for p in other_attacking_pieces], default=0)

        # succeeds if...
        if min_attack_strength > opposing_max_defend:
            if other_attacking_pieces:
                if min_attack_strength > other_pieces_max_prevent:
                    return self.set_outcome(Outcomes.SUCCEEDS)
            else:
                return self.set_outcome(Outcomes.SUCCEEDS)

        # fails if...
        if max_attack_strength <= opposing_min_defend:
            return self.set_outcome(Outcomes.FAILS)
        if max_attack_strength <= other_pieces_min_prevent:
            return self.set_outcome(Outcomes.FAILS)

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

    def to_dict(self):
        data = super().to_dict()
        return data


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

    def update_support_decision(self):
        piece = self.piece
        target_piece = self.target.piece
        aux_piece = self.aux.piece
        aux_target = getattr(self.aux.piece.order, 'target', None)

        source_attacking_pieces = self.source.other_attacking_pieces(target_piece)

        if piece.dislodged_decision == Outcomes.DISLODGED:
            return self.set_outcome(Outcomes.FAILS)

        # succeeds if...
        if piece.dislodged_decision == Outcomes.SUSTAINS:

            if not self.source.attacking_pieces:
                return self.set_outcome(Outcomes.SUCCEEDS)

            if target_piece and aux_piece:
                # If the aux piece is moving to the right target.
                if aux_piece.order.is_move and aux_target == self.target:
                    # If no pieces (other than the target piece) have strength
                    if all([p.order.attack_strength_decision.max_strength == 0 for p in source_attacking_pieces]):
                        return self.set_outcome(Outcomes.SUCCEEDS)

            if all([p.order.attack_strength_decision.max_strength == 0 for p in self.source.attacking_pieces]):
                return self.set_outcome(Outcomes.SUCCEEDS)

        # fails if...
        # If aux piece is not going to target of order
        if aux_piece:
            if aux_piece.order.is_move \
                    and aux_piece.order.target != self.target \
                    and aux_piece.order.legal:
                return self.set_outcome(Outcomes.FAILS)
            # If aux piece holds and support target is not same as aux
            if not aux_piece.order.is_move:
                if self.target != self.aux:
                    return self.set_outcome(Outcomes.FAILS)

        if target_piece and aux_piece:
            if aux_piece.order.is_move and aux_piece == self.target:
                if target_piece.order.is_convoy:
                    convoying_order = target_piece.order
                    if convoying_order.aux.piece:
                        if any([p.order.min_attack_strength >= 1
                                for p in self.source.other_attacking_pieces(convoying_order.aux.piece)]):
                            return self.set_outcome(Outcomes.FAILS)
                else:
                    if any([p.order.attack_strength_decision.min_strength >= 1
                            for p in self.source.other_attacking_pieces(self.target.piece)]):
                        return self.set_outcome(Outcomes.FAILS)

        if self.source.attacking_pieces and \
                any([p.order.attack_strength_decision()[0] >= 1
                     for p in self.source.attacking_pieces
                     if p.territory != aux_target]):
            return self.set_outcome(Outcomes.FAILS)

    def to_dict(self):
        data = super().to_dict()
        data.update({'outcome': self.outcome})
        return data


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

    def update_move_decision(self):

        piece = self.piece
        other_retreating_pieces = self.target.other_retreating_pieces(piece)

        if other_retreating_pieces:
            self.set_outcome(Outcomes.FAILS)
        else:
            self.set_outcome(Outcomes.SUCCEEDS)

    def to_dict(self):
        data = super().to_dict()
        return data


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

    def to_dict(self):
        if self.illegal:
            outcome = Outcomes.FAILS
        else:
            outcome = Outcomes.SUCCEEDS
        return {
            'id': self.id,
            'illegal': self.illegal,
            'illegal_verbose': self.illegal_verbose,
            'outcome': outcome,
        }

    def __str__(self):
        order_type = self.p__class__.__name__.upper()
        return f'{self.nation} - {order_type} {self.piece_type} {self.source}'


class Disband(Order):

    checks = [
        check.SourcePieceBelongsToNation,
    ]

    def to_dict(self):
        if self.legal_decision == Outcomes.ILLEGAL:
            outcome = Outcomes.FAILS
        else:
            outcome = Outcomes.SUCCEEDS
        return {
            'id': self.id,
            'legal_decision': self.legal_decision,
            'illegal_verbose': self.illegal_verbose,
            'outcome': outcome,
        }

    def __str__(self):
        order_type = self.p__class__.__name__.upper()
        return f'{self.nation} - {order_type} {self.piece_type} {self.source}'
