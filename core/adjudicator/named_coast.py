from .state import state


class NamedCoast:

    def __init__(self, id, name, parent, neighbours):
        state.all_named_coasts.append(self)
        self.id = id
        self.name = name
        self.parent = parent
        self.neighbours = neighbours

    def __str__(self):
        return f"{self.parent.name} ({self.name})"
