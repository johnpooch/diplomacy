from .state import register


class NamedCoast:

    @register
    def __init__(self, state, id, name, parent, neighbours):
        self.state = state
        self.id = id
        self.name = name
        self.parent = parent
        self.neighbour_ids = neighbours

    def __str__(self):
        return f"{self.parent.name} ({self.name})"

    @property
    def neighbours(self):
        return [t for t in self.state.territories if t.id in self.neighbour_ids]
