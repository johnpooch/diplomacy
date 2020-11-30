from .base import Decision, Outcomes


class Path(Decision):
    """
    For each piece ordered to move, the decision whether there is a path from
    the source to the destination. This decision will result in `path` or
    `no_path`. When the move is without any convoy, the decision always results
    in 'path'.
    """

    def _resolve(self):
        if not self.order.legal:
            return Outcomes.NO_PATH

        if not self.order.via_convoy:
            return Outcomes.PATH

        chains = self.order.convoy_chains

        if not chains:
            self.message = 'no convoy route available for move.'
            return Outcomes.NO_PATH

        for chain in chains:
            chain.resolve()

        if any([c.result == Outcomes.SUCCEEDS for c in chains]):
            return Outcomes.PATH

        if all([c.result == Outcomes.FAILS for c in chains]):
            self.message = 'convoy route was disrupted.'
            return Outcomes.NO_PATH

        return Outcomes.UNRESOLVED
