# TODO Come up with some sort of registry to allow for many to many
# relationships between territories. Look into observer pattern


class Territory:

    def __init__(self, name, nationality):
        self.name = name
        self.nationality = nationality
        self.neighbours = []


class LandTerritory(Territory):
    pass


class CoastalTerritory(LandTerritory):

    def __init__(self, name, nationality):
        super().__init__(name, nationality)
        self.shared_coasts = []


class InlandTerritory(LandTerritory):
    pass


class ComplexTerritory(CoastalTerritory):
    def __init__(self, name, nationality):
        super().__init__(name, nationality)
        self.named_coasts = []


class SeaTerritory(Territory):
    pass
