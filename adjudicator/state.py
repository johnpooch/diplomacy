class State:

    def __init__(self):
        self.subscribers = set()

    def register(self, *observers):
        for observer in observers:
            self.subscribers.add(observer)

    @property
    def territories(self):
        from adjudicator.territory import Territory
        return [t for t in self.subscribers if isinstance(t, Territory)]

    @property
    def pieces(self):
        from adjudicator.piece import Piece
        return [p for p in self.subscribers if isinstance(p, Piece)]

    @property
    def orders(self):
        from adjudicator.order import Order
        return [p for p in self.subscribers if isinstance(p, Order)]

    @property
    def named_coasts(self):
        from adjudicator.named_coast import NamedCoast
        return [s for s in self.subscribers if isinstance(s, NamedCoast)]

    def get_territory(self, name):
        return next(
            iter(t for t in self.territories if t.name == name),
            None
        )

    def get_territory_by_id(self, id):
        return next(
            iter(t for t in self.territories if t.id == id),
            None
        )

    def get_named_coast_by_id(self, id):
        return next(
            iter(n for n in self.named_coasts if n.id == id),
            None
        )


def register(init):
    """
    Decorator which handles registering instances to the state.
    """
    def register_instance(self, state, *args, **kwargs):
        init(self, state, *args, **kwargs)
        state.register(self)
    return register_instance
