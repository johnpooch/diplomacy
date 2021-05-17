from adjudicator.decisions.base import Outcomes
from . import decisions
from .state import register


class Territory:
    is_complex = False
    is_coastal = False
    is_inland = False
    is_sea = False

    @register
    def __init__(self, state, id, name, neighbours, contested=False, **kwargs):
        self.state = state
        self.id = id
        self.name = name
        self.neighbour_ids = neighbours
        self.contested = contested
        self.bounce_occurred = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} - {self.__class__.__name__}'

    @property
    def neighbours(self):
        return [t for t in self.state.territories if t.id in self.neighbour_ids]

    @property
    def pieces(self):
        return [p for p in self.state.pieces if p.territory == self]

    @property
    def attacking_pieces(self):
        from adjudicator.order import Move
        return [o.piece for o in self.state.orders if isinstance(o, Move)
                and o.target == self and o.piece]

    @property
    def retreating_pieces(self):
        from adjudicator.order import Retreat
        return [o.piece for o in self.state.orders if isinstance(o, Retreat)
                and o.target == self and o.piece]

    @property
    def named_coasts(self):
        return [s for s in self.state.named_coasts if s.parent == self]

    @property
    def piece(self):
        pieces = list(self.pieces)
        if len(pieces) == 1:
            return pieces[0]
        if len(pieces) == 2:
            return [p for p in pieces if p.retreating][0]
        if not pieces:
            return None

    @property
    def non_retreating_piece(self):
        pieces = list(self.pieces)
        if len(pieces) == 1:
            return pieces[0]
        if len(pieces) == 2:
            return [p for p in pieces if not p.retreating][0]
        if not pieces:
            return None

    @property
    def hold_strength(self):
        return decisions.HoldStrength(self)()

    @property
    def occupied(self):
        return bool(self.piece)

    @property
    def occupied_after_processing(self):
        """
        Whether the territory will be occupied after orders are processed.
        Used to determine if pieces can retreat here.
        """
        if any([p.order.outcome == Outcomes.SUCCEEDS for p in self.attacking_pieces]):
            return False
        if self.piece:
            return not (
                (self.piece.order.is_move and self.piece.order.outcome == Outcomes.SUCCEEDS)
                or (self.piece.destroyed)
            )
        return False

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
        return [p for p in self.attacking_pieces if p != piece]

    def other_retreating_pieces(self, piece):
        """
        Gets all pieces which are retreating into this territory excluding the
        given piece.

        Args:
            * `piece` - `Piece`

        Returns:
            * `list` of `Piece` instances.
        """
        return [p for p in self.retreating_pieces if p != piece]

    def to_dict(self):
        return {
            'id': self.id,
            'bounce_occurred': self.bounce_occurred,
        }


class LandTerritory(Territory):

    def __init__(self, state, id, name, nationality, neighbours, supply_center=False, controlled_by=None, **kwargs):
        super().__init__(state, id, name, neighbours, **kwargs)
        self.nationality = nationality
        self.supply_center = supply_center
        self.controlled_by = controlled_by
        self.captured_by = None


class CoastalTerritory(LandTerritory):

    is_coastal = True

    def __init__(self, state, id, name, nationality, neighbours, shared_coasts, **kwargs):
        super().__init__(state, id, name, nationality, neighbours, **kwargs)
        self.shared_coast_ids = shared_coasts

    @staticmethod
    def accessible_by_piece_type(piece):
        return True

    @property
    def shared_coasts(self):
        return [t for t in self.state.subscribers
                if isinstance(t, Territory) and t.id in self.shared_coast_ids]

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
