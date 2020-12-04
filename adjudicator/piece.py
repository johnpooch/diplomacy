from adjudicator.decisions import Outcomes
from .state import register


class PieceTypes:
    ARMY = 'army'
    FLEET = 'fleet'


class Piece:

    is_army = False
    is_fleet = False

    @register
    def __init__(self, state, id, nation, territory, attacker_territory=None,
                 retreating=False, **kwargs):
        self.state = state
        self.id = id
        self.nation = nation
        self.territory = territory
        self.dislodged_decision = Outcomes.UNRESOLVED
        self.dislodged_by = None
        self.attacker_territory = attacker_territory
        self.retreating = retreating
        self.destroyed = False
        self.destroyed_message = None

    def __str__(self):
        return f'{self.__class__.__name__} {self.territory}'

    def __repr__(self):
        return f'{self.__class__.__name__} {self.territory}'

    @property
    def order(self):
        from adjudicator.order import DummyHold
        return next(
            iter([
                o for o in self.state.orders
                if o.source == self.territory
                and o.nation == self.nation
            ]),
            DummyHold(self.state, self.nation, self.territory)
        )

    @property
    def moves(self):
        """
        Whether the piece's order is a successful move.

        Returns:
            * `bool`
        """
        if self.order.is_move:
            return self.order.outcome == Outcomes.SUCCEEDS
        return False

    @property
    def stays(self):
        """
        Whether the piece's order is a failing move or any other type of order,
        i.e. the piece does not move.

        Returns:
            * `bool`
        """
        if self.order.is_move:
            return self.order.outcome == Outcomes.FAILS
        return True

    @property
    def all_attacking_pieces_fail(self):
        """
        Whether every piece attacking this piece's territory fails. True if
        there are no attacking pieces.
        """
        attacking_pieces = list(self.territory.attacking_pieces)
        return all(
            [p.order.outcome == Outcomes.FAILS for p in attacking_pieces]
        )

    @property
    def successful_attacking_pieces(self):
        """
        Whether any piece attacking this piece's territory moves.
        """
        attacking_pieces = list(self.territory.attacking_pieces)
        return [p for p in attacking_pieces if p.order.outcome == Outcomes.SUCCEEDS]

    @property
    def dislodged(self):
        return self.dislodged_decision == Outcomes.DISLODGED

    def set_dislodged_decision(self, outcome, dislodged_by=None):
        self.dislodged_decision = outcome
        self.dislodged_by = dislodged_by
        if dislodged_by:
            if not dislodged_by.order.via_convoy:
                self.attacker_territory = dislodged_by.territory
        return self.dislodged_decision

    def update_dislodged_decision(self):
        """
        Determine whether the piece is dislodged.

        Returns:
            * `str` - dislodged decision
        """
        if self.moves or self.all_attacking_pieces_fail:
            return self.set_dislodged_decision(Outcomes.SUSTAINS)
        if self.successful_attacking_pieces:
            piece = self.successful_attacking_pieces[0]
            return self.set_dislodged_decision(Outcomes.DISLODGED, piece)
        return Outcomes.UNRESOLVED

    def can_retreat(self):
        """
        Determine whether the piece can retreat to any neighboring territory.

        Returns:
            * `bool`
        """
        for territory in self.territory.neighbours:
            accessible = territory.accessible_by_piece_type(self)
            unoccupied = not territory.occupied
            uncontested = not territory.bounce_occurred
            if accessible and unoccupied and uncontested:
                return True
        return False


class Army(Piece):

    is_army = True

    def can_reach(self, target, *args):
        """
        Determines whether the army can reach the given territory, regardless
        of whether the necessary convoying fleets exist or not.

        Args:
            * `target` - `territory`

        Returns:
            * `bool`
        """

        if self.territory.is_coastal and target.is_coastal:
            return True

        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)

    def can_reach_support(self, target):
        """
        Determines whether the army can reach the given territory in the
        context of providing support. Cannot provide support through a convoy.

        * Args:
            * `target` - `territory`

        Returns:
            * `bool`
        """
        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)


class Fleet(Piece):

    is_fleet = True

    def __init__(self, state, id, nation, territory, named_coast=None, retreating=False):
        super().__init__(state, id, nation, territory, retreating=retreating)
        self.named_coast = named_coast

    def can_reach(self, target, named_coast=None):
        """
        Determines whether the fleet can reach the given territory and named
        coast.

        Args:
            * `target` - `Territory`
            * `[named_coast]` - `NamedCoast`

        Returns:
            * `bool`
        """
        if target.is_complex and not named_coast:
            raise ValueError(
                'Must specify coast if target is complex territory.'
            )
        if named_coast:
            return self.territory in named_coast.neighbours

        if self.territory.is_complex:
            return target in self.named_coast.neighbours

        if self.territory.is_coastal and target.is_coastal:
            return target in self.territory.shared_coasts

        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)

    def can_reach_support(self, target):
        """
        Determines whether the fleet can reach the given territory in the
        context of providing support. In this context the fleet does not need
        to be able to reach the target named coast.

        * Args:
            * `target` - `territory`

        Returns:
            * `bool`
        """
        if self.territory.is_complex:
            return target in self.named_coast.neighbours

        if self.territory.is_coastal and target.is_coastal:
            return target in self.territory.shared_coasts

        return self.territory.adjacent_to(target) and \
            target.accessible_by_piece_type(self)
