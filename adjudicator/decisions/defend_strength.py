from .base import Decision, Outcomes


class DefendStrength(Decision):
    """
    For each piece ordered to move in a head to head battle, the strength to
    defend its own territory from the other piece of the head to head battle. A
    decision that results in a value equal or greater than zero.
    """
    def _resolve(self):
        return self._minimum(), self._maximum()

    def _minimum(self):
        return 1 + len(self.order.move_support(Outcomes.GIVEN))

    def _maximum(self):
        return 1 + len(self.order.move_support(Outcomes.GIVEN, Outcomes.UNRESOLVED))
