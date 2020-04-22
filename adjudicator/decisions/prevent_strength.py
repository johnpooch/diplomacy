from .base import Decision, Outcomes


class PreventStrength(Decision):
    """
    A numerical decision for each unit ordered to move. It is the strength to
    prevent other units to move to the area where it is ordered to move. A
    decision that results in a value equal or greater than zero.
    """
    min_strength = 0
    max_strength = 50

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
        if self.order.path_decision() in [Outcomes.NO_PATH, Outcomes.UNRESOLVED]:
            return 0
        if self.order.is_head_to_head():
            opposing_order = self.order.target.piece.order
            if opposing_order.move_decision in [Outcomes.MOVES, Outcomes.UNRESOLVED]:
                return 0
        return 1 + len(self.order.move_support(Outcomes.GIVEN))

    def _maximum(self):
        if self.order.path_decision() == Outcomes.NO_PATH:
            return 0
        if self.order.is_head_to_head():
            opposing_order = self.order.target.piece.order
            if opposing_order.move_decision == Outcomes.MOVES:
                return 0
        return 1 + len(self.order.move_support(Outcomes.GIVEN, Outcomes.UNRESOLVED))
