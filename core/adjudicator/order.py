from .state import state


class Order:

    def __init__(self, nation, source):
        state.all_orders.append(self)
        self.nation = nation
        self.source = source
        self._piece = None
        self._piece_cached = False

    @property
    def piece(self):
        """
        Gets the `Piece` instance which exists in `self.source` or `None` if
        there is no piece in the territory.

        Returns:
            * `Piece` or `None`
        """
        if not self._piece_cached:
            for p in state.all_pieces:
                if p.territory == self.source:
                    self._piece = p
            self._piece_cached = True
        return self._piece


class Hold(Order):
    pass


class Move(Order):
    def __init__(self, nation, source, target, via_convoy=False):
        super().__init__(nation, source)
        self.target = target
        self.via_convoy = via_convoy


class Support(Order):
    def __init__(self, nation, source, aux, target):
        super().__init__(nation, source)
        self.aux = aux
        self.target = target


class Convoy(Order):
    def __init__(self, nation, source, aux, target):
        super().__init__(nation, source)
        self.aux = aux
        self.target = target
