
""" This script contains the territory class and subclasses. Special coastal and special inland territories represent the 
    three territories which have two separate coasts. Special coasta inheritx from the Water class becasue they share
    a lot of functionality. """
# import is at the bottom of thew script. this feels hacky to me.

# Territory =======================================================================================

class Territory():
    all_territories = []
    def __init__(self, name, display_name, neighbours):  # 
        Territory.all_territories.append(self) # 
        self.name = name
        self.display_name = display_name
        self.neighbours = neighbours
        
    def occupied(self):
        return any([piece.territory == self for piece in Piece.all_pieces])
        
    def has_supply_center_which_belongs_to_player(self):
        return True
            
    def find_other_pieces_challenging_territory(self, piece):
        return [other_piece for other_piece in Piece.all_pieces if other_piece.challenging == self and id(piece) != id(other_piece)]

    def __repr__(self):
        return "{}, {}".format(self.name, self.display_name)
        
    def __str__(self):
        return "Name: {}, Display Name: {}".format(self.name, self.display_name)
        
# Water -------------------------------------------------------------------------------------------
        
class Water(Territory):
    def __init__(self, name, display_name, neighbours):
        Territory.__init__(self, name, display_name, neighbours)
        self.supply_center = False
        
    def accessible_by_piece_type(self, piece):
        return isinstance(piece, Fleet)
        
# Coastal -----------------------------------------------------------------------------------------
        
class Coastal(Territory):
    def __init__(self, name, display_name, neighbours, shared_coasts, supply_center):
        Territory.__init__(self, name, display_name, neighbours)
        self.shared_coasts = shared_coasts
        self.supply_center = supply_center
        
    def accessible_by_piece_type(self, piece):
            return isinstance(piece, Army) or (self.shares_coast_with_piece(piece) or isinstance(piece.territory, Water))
        
    def shares_coast_with_piece(self, piece):
        return piece.territory in self.shared_coasts
        
# Inland ------------------------------------------------------------------------------------------
        
class Inland(Territory):
    def __init__(self, name, display_name, neighbours, supply_center):
        Territory.__init__(self, name, display_name, neighbours)
        self.supply_center = supply_center
        
    def accessible_by_piece_type(self, piece):
        return isinstance(piece, Army)
        
# Special Inland ----------------------------------------------------------------------------------
        
class Special_Inland(Inland):
    def __init__(self, name, display_name, neighbours, supply_center, coasts):
        Inland.__init__(self, name, display_name, neighbours, supply_center)
        self.coasts = coasts
        
    def occupied(self):
        return any([piece.territory == self or self.coasts for piece in Piece.all_pieces])
        
    def find_other_pieces_challenging_territory(self, piece):
        other_piece_list = []
        for other_piece in Piece.all_pieces:
            if other_piece.challenging == self and id(piece) != id(other_piece):
                other_piece_list.append(other_piece)
            for coast in self.coasts:
                if other_piece.challenging == coast and id(piece) != id(other_piece):
                    other_piece_list.append(other_piece)
        return other_piece_list
        
# Special Coastal ---------------------------------------------------------------------------------
        
class Special_Coastal(Water):
    def __init__(self, name, display_name, neighbours, parent_territory):
        Water.__init__(self, name, display_name, neighbours)
        self.parent_territory = parent_territory
        
    def occupied(self):
        return any([piece.territory == self or self.parent_territory for piece in Piece.all_pieces])
        
    def find_other_pieces_challenging_territory(self, piece):
        return [other_piece for other_piece in Piece.all_pieces if other_piece.challenging == self or other_piece.challenging == self.parent_territory and id(piece) != id(other_piece)]
        
from piece import *
