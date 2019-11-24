# relationships between territories. Look into observer pattern


class Territory:

    all_territories = []

    def __init__(self, id, name, nationality, neighbour_ids):
        self.id = id
        self.name = name
        self.nationality = nationality
        self.neighbour_ids = neighbour_ids
        self._neighbours = []
        self.__class__.all_territories.append(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} - {self.__class__.__name__}'

    @property
    def neighbours(self):
        """
        Gets the neighbours of the territory. Neighbours are cached in the
        `self._neighbours` attribute. This avoids unnecessary iteration because
        the neighbours of a territory never change during adjudication.

        Returns:
            * A list of `Territory` instances.
        """
        if not self._neighbours:
            for t in self.__class__.all_territories:
                if t.id in self.neighbour_ids:
                    self._neighbours.append(t)
        return self._neighbours

    def adjacent_to(self, territory):
        return territory in self.neighbours


class LandTerritory(Territory):
    pass


class CoastalTerritory(LandTerritory):

    def __init__(self, id, name, nationality, neighbour_ids, shared_coast_ids):
        super().__init__(id, name, nationality, neighbour_ids)
        self.shared_coast_ids = shared_coast_ids
        self._shared_coasts = []

    @property
    def shared_coasts(self):
        """
        Gets the shared_coasts of the territory. Neighbours are cached in the
        `self._shared_coasts` attribute. This avoids unnecessary iteration because
        the neighbours of a territory never change during adjudication.

        Returns:
            * A list of `Territory` instances.
        """
        if not self._shared_coasts:
            for t in self.__class__.all_territories:
                if t.id in self.shared_coast_ids:
                    self._shared_coasts.append(t)
        return self._shared_coasts


class InlandTerritory(LandTerritory):
    pass


class ComplexTerritory(CoastalTerritory):

    def __init__(self, id, name, nationality, neighbour_ids, shared_coast_ids,
                 named_coast_ids):
        super().__init__(id, name, nationality, neighbour_ids, shared_coast_ids)
        self.named_coast_ids = named_coast_ids


class SeaTerritory(Territory):
    pass
