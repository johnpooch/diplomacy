from .order import Hold, Order


class Piece:
    all_pieces = []

    def __init__(self, nation, territory):
        self.__class__.all_pieces.append(self)
        self.nation = nation
        self.territory = territory
        self._order = None

    @property
    def order(self):
        """
        Gets the `Order` which is assigned to this piece.
        Returns:
            * `Order`
        """

        if not self._order:
            for o in Order.all_orders:
                if o.source == self.territory:
                    self._order = o
            if not self._order:
                self._order = Hold(self.nation, self.territory)

        return self._order


class Army(Piece):
    pass


class Fleet(Piece):
    def __init__(self, nation, territory, named_coast=None):
        super().__init__(nation, territory)  # DRY - do not repeat yourself
        self.named_coast = named_coast
