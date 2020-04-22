class NamedCoast:

    def __init__(self, _id, name, parent, neighbours):
        self.id = _id
        self.name = name
        self.parent = parent
        self.neighbours = neighbours

    def __str__(self):
        return f"{self.parent.name} ({self.name})"
