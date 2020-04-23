from .base import Decision, Outcomes
from .path import Path


class AttackStrength(Decision):
    """
    For each unit ordered to move, the strength to attack. A decision that
    results in a value equal or greater than zero.
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
        path = Path(self.order)()

        if path == Outcomes.NO_PATH:
            return 0

        if not self.order.target.piece or self.order.target.piece.moves:
            return 1 + len(self.order.move_support(Outcomes.GIVEN))

        if self.order.is_head_to_head() or not self.order.target.piece.moves:
            if self.order.target.piece.nation == self.order.nation:
                return 0
            return 1 + len([c for c in self.order.move_support(Outcomes.GIVEN)
                            if c.nation != self.order.target.piece.nation])

        return 1 + len(self.order.move_support(Outcomes.GIVEN))

    def _maximum(self):
        path = Path(self.order)()

        if path == Outcomes.NO_PATH:
            return 0

        if not self.order.target.piece or self.order.target.piece.moves:
            return 1 + len(self.order.move_support(Outcomes.GIVEN, Outcomes.UNRESOLVED))

        if self.order.is_head_to_head() or self.order.target.piece.stays:
            if self.order.target.piece.nation == self.order.nation:
                return 0
            return 1 + len([c for c in self.order.move_support(Outcomes.GIVEN, Outcomes.UNRESOLVED)
                            if c.nation != self.order.target.piece.nation])

        return 1 + len(self.order.move_support(Outcomes.GIVEN, Outcomes.UNRESOLVED))
