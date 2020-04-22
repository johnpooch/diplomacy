from .base import Decision, Outcomes


class HoldStrength(Decision):
    """
    For each territory on the board the strength to prevent that other pieces
    move to that territory. A decision that results in a value equal or greater
    than zero.
    """
    min_strength = 0
    max_strength = 50

    def __init__(self, territory):
        self.territory = territory
        self.result = Outcomes.UNRESOLVED

    def __call__(self):
        """
        Return the result of the min and max strength if resolved (if both
        values are equal then it is resolved). Otherwise attempt to resolve the
        decision and then return the result.

        Returns:
            * `tuple` - min strength and max strength
        """
        if self.min_strength == self.max_strength:
            return self.min_strength, self.max_strength
        self.min_strength, self.max_strength = self._resolve()
        return self.min_strength, self.max_strength

    def _resolve(self):
        return self._minimum(), self._maximum()

    def _minimum(self):
        piece = self.territory.piece

        if not piece:
            return 0

        if piece.order.is_move:
            if piece.order.move_decision == Outcomes.FAILS:
                return 1
            return 0

        return 1 + len(piece.order.hold_support(Outcomes.GIVEN))

    def _maximum(self):
        piece = self.territory.piece

        if not piece:
            return 0

        if piece.order.is_move:
            if piece.order.move_decision == Outcomes.MOVES:
                return 0
            return 1

        return 1 + len(piece.order.hold_support(Outcomes.GIVEN, Outcomes.UNRESOLVED))
