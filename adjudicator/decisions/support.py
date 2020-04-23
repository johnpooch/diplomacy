from .base import Decision, Outcomes
from .attack_strength import AttackStrength


class Support(Decision):
    """
    For each piece ordered to support, the decision whether the support is
    given or cut.
    """
    def _resolve(self):
        pass

