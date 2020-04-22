from . import decisions


class Territory:
    is_complex = False
    is_coastal = False
    is_inland = False
    is_sea = False

    def __init__(self, _id, name, neighbour_ids, contested=False):
        self.id = _id
        self.name = name
        self.neighbour_ids = neighbour_ids

        self.piece = None
        self.neighbours = set()
        self.named_coasts = set()
        self.attacking_pieces = set()
        self.retreating_pieces = set()
        self.contested = contested

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} - {self.__class__.__name__}'

    @property
    def hold_strength(self):
        return decisions.HoldStrength(self)()

    @property
    def occupied(self):
        return bool(self.piece)

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
        foreign_attacking_pieces = list(self.attacking_pieces)
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
        other_attacking_pieces = list(self.attacking_pieces)
        for p in other_attacking_pieces:
            if p == piece:
                other_attacking_pieces.remove(p)
        return other_attacking_pieces

    def other_retreating_pieces(self, piece):
        """
        Gets all pieces which are retreating into this territory excluding the
        given piece.

        Args:
            * `piece` - `Piece`

        Returns:
            * `list` of `Piece` instances.
        """
        other_retreating_pieces = list(self.retreating_pieces)
        return [p for p in other_retreating_pieces if p != piece]

    def to_dict(self):
        return {
            'id': self.id,
            'contested': self.contested,
        }


class LandTerritory(Territory):

    def __init__(self, _id, name, nationality, neighbour_ids, supply_center=False, controlled_by=None):
        super().__init__(_id, name, neighbour_ids)
        self.nationality = nationality
        self.supply_center = supply_center
        self.controlled_by = controlled_by


class CoastalTerritory(LandTerritory):

    is_coastal = True

    def __init__(self, _id, name, nationality, neighbour_ids, shared_coast_ids, supply_center=False, controlled_by=None):
        super().__init__(_id, name, nationality, neighbour_ids, supply_center, controlled_by)
        self.shared_coast_ids = shared_coast_ids
        self.shared_coasts = set()

    @staticmethod
    def accessible_by_piece_type(piece):
        return True

    @property
    def is_complex(self):
        return bool(self.named_coasts)


class InlandTerritory(LandTerritory):

    is_inland = True

    @staticmethod
    def accessible_by_piece_type(piece):
        return piece.__class__.__name__ == 'Army'


class SeaTerritory(Territory):

    is_sea = True

    @staticmethod
    def accessible_by_piece_type(piece):
        return piece.__class__.__name__ == 'Fleet'
