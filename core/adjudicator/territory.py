# relationships between territories. Look into observer pattern
from .state import state


class Territory:
    is_complex = False
    is_coastal = False

    def __init__(self, id, name, neighbour_ids):
        state.all_territories.append(self)
        self.id = id
        self.name = name
        self.neighbour_ids = neighbour_ids
        self._neighbours = []
        self._piece = None
        self._piece_cached = False
        self._attacking_pieces = []
        self._attacking_pieces_cached = False

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
            self._named_coasts_cached = True
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

    @property
    def attacking_pieces(self):
        """
        Gets all pieces which are moving into this territory.

        Returns:
            * `list` of `Piece` instances
        """
        if self._attacking_pieces_cached:
            return self._attacking_pieces

        for p in state.all_pieces:
            if p.order.__class__.__name__ == 'Move':
                if p.order.target == self:
                    self._attacking_pieces.append(p)
        self._attacking_pieces_cached = True
        return self._attacking_pieces

    def adjacent_to(self, territory):
        return territory in self.neighbours

    def friendly_piece_exists(self, nation):
        """
        Determine whether a piece belonging to the given nation exists in the
        territory.

        Args:
            * `nation` - `str`

        Returns:
            * `bool`
        """
        if self.piece:
            return self.piece.nation == nation
        return False

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

    def foreign_attacking_pieces(self, nation):
        """
        Gets all pieces which are moving into this territory
        who do not belong to the given.
        Args:
            * `nation` - `str`

        Returns a list of piece instances
        """
        foreign_attacking_pieces = self.attacking_pieces
        for p in foreign_attacking_pieces:
            if p.nation == nation:
                foreign_attacking_pieces.remove(p)
        return foreign_attacking_pieces

    def other_attacking_pieces(self, piece):
        """
        Gets all pieces which are moving into this territory excluding the
        given piece.

        Args:
            * `piece` - `Piece`

        Returns:
            * `list` of `Piece` instances.
        """
        other_attacking_pieces = self.attacking_pieces
        for p in other_attacking_pieces:
            if p == piece:
                other_attacking_pieces.remove(p)
        return other_attacking_pieces


class LandTerritory(Territory):

    def __init__(self, id, name, nationality, neighbour_ids,
                 supply_center=False):
        super().__init__(id, name, neighbour_ids)
        self.nationality = nationality
        self.supply_center = supply_center


class CoastalTerritory(LandTerritory):

    is_coastal = True

    def __init__(self, id, name, nationality, neighbour_ids, shared_coast_ids):
        super().__init__(id, name, nationality, neighbour_ids)
        self.shared_coast_ids = shared_coast_ids
        self._shared_coasts = []
        self._named_coasts_cached = False
        self._named_coasts = []

    @property
    def named_coasts(self):
        """
        Gets the named coasts of the territory.

        Returns:
            * A list of `Named_Coast` instances.
        """
        if not self._named_coasts_cached:
            for n in state.all_named_coasts:
                if n.parent == self:
                    self._named_coasts.append(n)
        return self._named_coasts

    @property
    def is_complex(self):
        return bool(self.named_coasts)

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
        return piece.__class__.__name__ == 'Army'


class SeaTerritory(Territory):

    @staticmethod
    def accessible_by_piece_type(piece):
        return piece.__class__.__name__ == 'Fleet'
