# relationships between territories. Look into observer pattern
from .state import state

from .piece import Army, Fleet


class Territory:

    def __init__(self, id, name, neighbour_ids):
        state.all_territories.append(self)
        self.id = id
        self.name = name
        self.neighbour_ids = neighbour_ids
        self._neighbours = []
        self._piece = None
        self._piece_cached = False

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
            for t in state.all_territories:
                if t.id in self.neighbour_ids:
                    self._neighbours.append(t)
        return self._neighbours

    @property
    def piece(self):
        """
        Gets the `Piece` instance which exists in the territory or `None` if
        there is no piece in the territory.

        Returns:
            * `Piece` or `None`
        """
        if not self._piece_cached:
            for p in state.all_pieces:
                if p.territory == self:
                    self._piece = p
            self._piece_cached = True
        return self._piece

    @property
    def occupied(self):
        return bool(self.piece)

    def adjacent_to(self, territory):
        return territory in self.neighbours

    def occupied_by(self, nation):
        """
        Determine whether the territory is occupied by a piece belonging to the given nation

         Args:
            * `nation` - `str`

        Returns:
            * `bool`

        """
        if self.occupied:
            return self.piece.nation == nation

        return False


class LandTerritory(Territory):

    def __init__(self, id, name, nationality, neighbour_ids,
                 supply_center=False):
        super().__init__(id, name, neighbour_ids)
        self.nationality = nationality
        self.supply_center = supply_center


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
            for t in state.all_territories:
                if t.id in self.shared_coast_ids:
                    self._shared_coasts.append(t)
        return self._shared_coasts

    def shares_coast_with(self, territory):
        return territory in self.shared_coasts

    @staticmethod
    def accessible_by_piece_type(piece):
        return True


class InlandTerritory(LandTerritory):

    @staticmethod
    def accessible_by_piece_type(piece):
        return isinstance(piece, Army)


class ComplexTerritory(CoastalTerritory):

    def __init__(self, id, name, nationality, neighbour_ids, shared_coast_ids,
                 named_coast_ids):
        super().__init__(id, name, nationality, neighbour_ids, shared_coast_ids)
        self.named_coast_ids = named_coast_ids


class SeaTerritory(Territory):

    @staticmethod
    def accessible_by_piece_type(piece):
        return isinstance(piece, Fleet)
