from write_to_log import write_to_log

# Piece ===========================================================================================

class Piece:
    all_pieces = []
    def __init__(self, territory, nation):
        Piece.all_pieces.append(self)
        self.territory = territory
        self.nation = nation
        self.order = None
        self.challenging = territory
        self.previous_territory = territory
        self.convoyed_by = []
        self.strength = {}
        self.retreat = False
        self.piece_type = ""
        
    def assign_piece_to_order(self):
        if self.order:
            self.order.piece = self
        
    def has_most_strength(self, challenging_pieces):
        for challenging_piece in challenging_pieces:
            # zero strength
            if not self.challenging in challenging_piece.strength:
                challenging_piece.strength[self.challenging] = 0
            if not self.challenging in self.strength:
                self.strength[self.challenging] = 0
            
        return all(self.strength[self.challenging] > challenging_piece.strength[self.challenging] for challenging_piece in challenging_pieces)
        
    def identify_retreats(self):
        challenging_pieces = self.challenging.find_other_pieces_challenging_territory(self)
        if self.has_most_strength(challenging_pieces):
            for challenging_piece in challenging_pieces:
                if challenging_piece.territory == challenging_piece.challenging:
                    write_to_log("piece at {0} must now retreat".format(challenging_piece.territory.name))
                    challenging_piece.must_retreat()
        
    def change_territory(self):
        self.previous_territory = self.territory
        self.challenging = self.challenging
        self.territory = self.challenging
        write_to_log("{} at {} has moved to {}".format(self.piece_type, self.previous_territory.name, self.territory.name))
        
    def find_other_piece_in_territory(self):
        for piece in Piece.all_pieces:
            if self.territory == piece.territory and id(self) != id(piece):
                return piece
        
    def can_retreat(self):
        return any([neighbour for neighbour in self.territory.neighbours if (not neighbour.occupied()) and neighbour.accessible_by_piece_type(self) and neighbour != self.find_other_piece_in_territory().previous_territory])
        
    def must_retreat(self):
        self.retreat = True
        
    def retreat_resolved(self):
        self.retreat = False
    
    def destroy(self):
        Piece.all_pieces.remove(self)
        if self in Army.all_armies:
            Army.all_armies.remove(self)
            write_to_log("\n{} at {} has been destroyed".format(self.piece_type, self.territory.name))
        if self in Fleet.all_fleets:
            Fleet.all_fleets.remove(self)
            write_to_log("\n{} at {} has been destroyed".format(self.piece_type, self.territory.name))
        
# Army --------------------------------------------------------------------------------------------
        
class Army(Piece):
    all_armies = []
    def __init__(self, territory, owner):
        Army.all_armies.append(self)
        Piece.__init__(self, territory, owner)
        self.piece_type = "army"
        

# Fleet -------------------------------------------------------------------------------------------

class Fleet(Piece):
    all_fleets = []
    def __init__(self, territory, owner):
        Fleet.all_fleets.append(self)
        Piece.__init__(self, territory, owner)
        self.piece_type = "fleet"
