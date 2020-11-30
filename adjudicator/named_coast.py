from .state import register


class NamedCoast:

    @register
    def __init__(self, state, id, name, parent, neighbours):
        self.id = id
        self.name = name
        self.parent = parent
        self.neighbours = neighbours

    def __str__(self):
        return f"{self.parent.name} ({self.name})"
