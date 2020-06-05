from . import decisions, check
from .decisions import Outcomes
from . import illegal_messages
from .decisions.attack_strength import AttackStrength
from .piece import PieceTypes


class Order:

    def __init__(self, _id, nation, source):
        self.id = _id
        self.nation = nation
        self.source = source
        self.piece = None
        self.hold_support_orders = set()
        self.legal_decision = Outcomes.LEGAL
        self.illegal_code = None
        self.illegal_message = None

    def __str__(self):
        return ' '.join(
            [
                self.nation,
                self.__class__.__name__.upper(),
                self.source.name,
            ]
        )

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

    def set_illegal(self, code, message):
        self.illegal_code = code
        self.illegal_message = message
        self.legal_decision = Outcomes.ILLEGAL
        return self.legal_decision

    def update_legal_decision(self):
        """
        Iterate through each legality check. If a check's fail_condition is
        satisfied, set the order to be illegal and set the illegal message.
        """
        for c in self.checks:
            if c().fail_condition(self):
                return self.set_illegal(c.code, c.message)

    def to_dict(self):
        if self.piece:
            if self.piece.dislodged_decision == Outcomes.DISLODGED:
                outcome = Outcomes.FAILS
            else:
                outcome = Outcomes.SUCCEEDS
        return {
            'id': self.id,
            'legal_decision': self.legal_decision,
            'illegal_message': self.illegal_message,
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

        self.move_decision = Outcomes.UNRESOLVED
        self.attack_strength_decision = decisions.AttackStrength(self)
        self.prevent_strength_decision = decisions.PreventStrength(self)
        self.defend_strength_decision = decisions.DefendStrength(self)
        self.path_decision = decisions.Path(self)

    def set_move_decision(self, outcome):
        self.move_decision = outcome
        return self.move_decision

    def update_move_decision(self):

        if self.path_decision() == Outcomes.NO_PATH:
            return self.set_move_decision(Outcomes.FAILS)

        if self.path_decision() == Outcomes.UNRESOLVED:
            return

        if self.is_head_to_head():
            return self._resolve_head_to_head()

        if self.is_convoy_swap():
            return self._resolve_convoy_swap()

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
                    return self.set_move_decision(Outcomes.MOVES)
        else:
            if min_attack_strength > target_max_hold:
                return self.set_move_decision(Outcomes.MOVES)

        # fails if...
        if max_attack_strength <= target_min_hold:
            return self.set_move_decision(Outcomes.FAILS)

        if other_attacking_pieces:
            if max_attack_strength <= other_pieces_min_prevent:
                return self.set_move_decision(Outcomes.FAILS)

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
                    return self.set_move_decision(Outcomes.MOVES)
            else:
                return self.set_move_decision(Outcomes.MOVES)

        # fails if...
        if max_attack_strength <= opposing_min_defend:
            return self.set_move_decision(Outcomes.FAILS)
        if max_attack_strength <= other_pieces_min_prevent:
            return self.set_move_decision(Outcomes.FAILS)

    def _convoy_swap_result(self):
        # TODO rename
        piece = self.piece
        min_attack_strength, max_attack_strength = AttackStrength(self)()

        other_attacking_pieces = self.target.other_attacking_pieces(piece)
        other_pieces_max_prevent = max([p.order.prevent_strength_decision()[1] for p in other_attacking_pieces], default=0)
        other_pieces_min_prevent = min([p.order.prevent_strength_decision()[0] for p in other_attacking_pieces], default=0)

        # succeeds if...
        if other_attacking_pieces:
            if min_attack_strength > other_pieces_max_prevent:
                return Outcomes.MOVES
        else:
            return Outcomes.MOVES

        # fails if...
        if other_attacking_pieces:
            if max_attack_strength <= other_pieces_min_prevent:
                return Outcomes.FAILS

        return Outcomes.UNRESOLVED

    def _resolve_convoy_swap(self):

        # both pieces must succeed
        swapping_piece = self.target.piece
        swapping_piece_order = swapping_piece.order

        this_result = self._convoy_swap_result()
        swapping_result = swapping_piece_order._convoy_swap_result()

        if this_result == swapping_result == Outcomes.MOVES:
            self.set_move_decision(Outcomes.MOVES)
            swapping_piece_order.set_move_decision(Outcomes.MOVES)
            return

        if this_result == Outcomes.FAILS or swapping_result == Outcomes.FAILS:
            self.set_move_decision(Outcomes.FAILS)
            swapping_piece_order.set_move_decision(Outcomes.FAILS)
            return

    def move_support(self, *args):
        legal_decisions = [Outcomes.LEGAL]
        return [s for s in self.move_support_orders if
                s.support_decision in args and s.legal_decision in legal_decisions]

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
                    if opposing_piece.order.legal_decision == Outcomes.LEGAL:
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
                    if opposing_piece.order.legal_decision == Outcomes.LEGAL:
                        if opposing_piece.order.path_decision() == Outcomes.PATH:
                            return opposing_piece.order.target == self.source
        return False

    def to_dict(self):
        data = super().to_dict()
        data.update({'outcome': self.move_decision})
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
        self.support_decision = Outcomes.UNRESOLVED

    def set_support_decision(self, outcome):
        self.support_decision = outcome
        return self.support_decision

    def update_support_decision(self):
        piece = self.piece
        target_piece = self.target.piece
        aux_piece = self.aux.piece
        aux_target = getattr(self.aux.piece.order, 'target', None)

        source_attacking_pieces = self.source.other_attacking_pieces(target_piece)
        if piece.dislodged_decision == Outcomes.UNRESOLVED:
            return self.set_support_decision(Outcomes.UNRESOLVED)

        if piece.dislodged_decision == Outcomes.DISLODGED:
            return self.set_support_decision(Outcomes.CUT)

        # succeeds if...
        if piece.dislodged_decision == Outcomes.SUSTAINS:

            if not self.source.attacking_pieces:
                return self.set_support_decision(Outcomes.GIVEN)

            if target_piece and aux_piece:
                # If the aux piece is moving to the right target.
                if aux_piece.order.is_move and aux_target == self.target:
                    # If no pieces (other than the target piece) have strength
                    if all([p.order.attack_strength_decision.max_strength == 0 for p in source_attacking_pieces]):
                        return self.set_support_decision(Outcomes.GIVEN)

            if all([p.order.attack_strength_decision.max_strength == 0 for p in self.source.attacking_pieces]):
                return self.set_support_decision(Outcomes.GIVEN)

                # # NOTE not sure what this block is for.
                # if isinstance(target_piece.order, Convoy):
                #     convoying_order = target_piece.order
                #     if convoying_order.aux.piece:
                #         if all([p.order.attack_strength == 0
                #                 for p in self.source.other_attacking_pieces(convoying_order.aux.piece)]):
                #             return Outcomes.GIVEN

        # fails if...
        # If aux piece is not going to target of order
        if aux_piece:
            if aux_piece.order.is_move \
                    and aux_piece.order.target != self.target \
                    and aux_piece.order.legal_decision == Outcomes.LEGAL:
                return self.set_support_decision(Outcomes.CUT)
            # If aux piece holds and support target is not same as aux
            if not aux_piece.order.is_move:
                if self.target != self.aux:
                    return self.set_support_decision(Outcomes.CUT)

        if target_piece and aux_piece:
            if aux_piece.order.is_move and aux_piece == self.target:
                if target_piece.order.is_convoy:
                    convoying_order = target_piece.order
                    if convoying_order.aux.piece:
                        if any([p.order.min_attack_strength >= 1
                                for p in self.source.other_attacking_pieces(convoying_order.aux.piece)]):
                            return self.set_support_decision(Outcomes.CUT)
                else:
                    if any([p.order.attack_strength_decision.min_strength >= 1
                            for p in self.source.other_attacking_pieces(self.target.piece)]):
                        return self.set_support_decision(Outcomes.CUT)

        if self.source.attacking_pieces and \
                any([p.order.attack_strength_decision()[0] >= 1
                     for p in self.source.attacking_pieces
                     if p.territory != aux_target]):
            return self.set_support_decision(Outcomes.CUT)

    def to_dict(self):
        data = super().to_dict()
        data.update({'outcome': self.support_decision})
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
        self.move_decision = Outcomes.UNRESOLVED

    def set_move_decision(self, outcome):
        self.move_decision = outcome
        return self.move_decision

    def update_move_decision(self):

        piece = self.piece
        other_retreating_pieces = self.target.other_retreating_pieces(piece)

        if other_retreating_pieces:
            self.set_move_decision(Outcomes.FAILS)
        else:
            self.set_move_decision(Outcomes.SUCCEEDS)

    def to_dict(self):
        data = super().to_dict()
        data.update({'outcome': self.move_decision})
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
        if self.legal_decision == Outcomes.ILLEGAL:
            outcome = Outcomes.FAILS
        else:
            outcome = Outcomes.SUCCEEDS
        return {
            'id': self.id,
            'legal_decision': self.legal_decision,
            'illegal_message': self.illegal_message,
            'outcome': outcome,
        }


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
            'illegal_message': self.illegal_message,
            'outcome': outcome,
        }
