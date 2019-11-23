"""
Mixin classes for ``Order`` and ``Territory`` which provide logic for
resolving decisions.
"""


class Decision:

    def _check_is_move(self):
        """
        Attack strength should only be determined for move orders. If this
        method if called for other types of order, something is wrong.
        """
        if not self.is_move:
            raise ValueError(
                f'{self.__class.__name__} decision should only be determined '
                'for move orders.'
            )


class AttackStrength(Decision):

    @property
    def min_attack_strength(self):
        """
        Determine the minimum attack strength of a move order.
        """
        self._check_is_move()

        if not self.move_path:
            return 0

        if not self.target.occupied() or self.target.piece.moves:
            return 1 + len(self.successful_support)

        if self.head_to_head_exists() or not self.target.piece.moves:
            if self.target.piece.nation == self.nation:
                return 0
            return 1 + len([c for c in self.successful_support
                            if c.nation != self.target.piece.nation])

        return 1 + len(self.successful_support)

    @property
    def max_attack_strength(self):
        """
        Determine the maximum attack strength of a move order.
        """
        self._check_is_move()

        if not self.move_path:
            return 0

        if not self.target.occupied() or self.target.piece.moves:
            return 1 + len(self.non_failing_support)

        if self.head_to_head_exists() or self.target.piece.stays:
            if self.target.piece.nation == self.nation:
                return 0
            return 1 + len([c for c in self.non_failing_support
                            if c.nation != self.target.piece.nation])

        return 1 + len(self.non_failing_support)


class DefendStrength(Decision):
    """
    For each unit ordered to move in a head to head battle, the strength to
    defend its own area from the other unit of the head to head battle.
    """

    @property
    def min_defend_strength(self):
        """
        Determine the minimum defend strength of a move order.
        """
        self._check_is_move()
        return 1 + len(self.successful_support)

    @property
    def max_defend_strength(self):
        """
        Determine the maximum defend strength of a move order.
        """
        self._check_is_move()
        return 1 + len(self.non_failing_support)


class PreventStrength(Decision):

    @property
    def min_prevent_strength(self):
        """
        Determine the minimum prevent strength of a move order.
        """
        self._check_is_move()

        if not self.move_path:  # should be no path or undecided
            return 0

        if self.head_to_head_exists():
            opposing_unit = self.target.piece
            if not opposing_unit.order.fails:
                return 0

        return 1 + len(self.successful_support)

    @property
    def max_prevent_strength(self):
        """
        Determine the maximum prevent strength of a move order.
        """
        self._check_is_move()

        if not self.move_path:  # should be no path
            return 0

        if self.head_to_head_exists():
            opposing_unit = self.target.piece
            if opposing_unit.order.succeeds:
                return 0

        return 1 + len(self.non_failing_support)


class HoldStrength(Decision):
    """
    For each territory on the board the strength to prevent that other pieces
    move to that territory.
    """

    @property
    def min_hold_strength(self):
        """
        Determine the minimum hold strength of a territory.
        """
        if not self.occupied():
            return 0

        if self.piece.order.is_move:
            if not self.piece.order.fails:
                return 0
            else:
                return 1 + len(self.piece.order.successful_hold_support)

        return 1 + len(self.piece.order.successful_support)

    @property
    def max_hold_strength(self):
        """
        Determine the maximum hold strength of a territory.
        """
        if not self.occupied():
            return 0

        if self.piece.moves:
            return 0
        if self.piece.order.is_move:
            return 1 + len(self.piece.order.non_failing_hold_support)

        return 1 + len(self.piece.order.non_failing_support)


class OrderDecisionsMixin(AttackStrength, DefendStrength, PreventStrength):
    """
    Allows ``Order`` to inherit one class rather than inheriting from each
    ``Decision`` class inidvidually.
    """
    pass
