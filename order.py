from territory import *
from game_properties import *

# Order ===========================================================================================

class Order():
    all_orders = []
    
    def __init__(self, player, territory):
        Order.all_orders.append(self)
        self.player = player
        self.territory = territory
        self.year = game_properties.year
        self.phase = game_properties.phase
        self.success = True
        self.report = ""
        self.bounced = False
        self.piece = None
        
    # Refactor?
    def identify_retreats(self):
        challenging_pieces = self.piece.challenging.find_other_pieces_challenging_territory(self.piece)
        if self.piece.has_most_strength(challenging_pieces):
            for challenging_piece in challenging_pieces:
                if challenging_piece.territory == challenging_piece.challenging:
                    write_to_log("piece at {0} must now retreat".format(challenging_piece.territory.name))
                    challenging_piece.must_retreat()
    
    def get_object_by_territory(self, territory):
        return [piece for piece in Piece.all_pieces if piece.territory.name == territory.name][0]

    def territory_is_neighbour(self, territory):
        neighbours = self.territory.neighbours
        return any(neighbour.name == territory.name for neighbour in neighbours)
            
    def fail(self, report_string):
        self.report = report_string
        self.success = False
        

# Hold --------------------------------------------------------------------------------------------

class Hold(Order):
    def __init__(self, player, territory):
        Order.__init__(self, player, territory)
        
    def process_order(self):
        pass
        
    def __repr__(self):
        return "{}, {}: Hold({}, {})".format(self.year, self.phase, self.player, self.territory)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, hold.".format(self.year, self.phase, self.territory.name, self.player)
        
        
# Convoy ------------------------------------------------------------------------------------------
        
class Convoy(Order):
    def __init__(self, player, territory, convoyed_territory, target):
        Order.__init__(self, player, territory)
        self.target = target
        self.convoyed_territory = convoyed_territory
        
    def piece_is_on_water(self):
        return isinstance(self.piece.territory, Water)
    
    def process_order(self):
        if self.piece_is_on_water():
            object_piece = self.get_object_by_territory(self.convoyed_territory)
            object_piece.convoyed_by = {self.piece: self.target}
            write_to_log("{} at {} is now convoying {} to {}".format(self.piece.piece_type, self.territory.name, object_piece.territory.name, self.target.name))
        else: 
            write_to_log("convoy failed: piece at {} must be on water to convoy".format(self.territory.name))
    
    def __repr__(self):
        return "{}, {}: Convoy({}, {}, {}, {})".format(self.year, self.phase, self.player, self.territory.name, self.convoyed_territory.name, self.target.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, convoy {} to {}.".format(self.year, self.phase, self.territory.name, self.player, self.convoyed_territory.name, self.target.name)
        
# Move --------------------------------------------------------------------------------------------

class Move(Order):
    all_moves = []
    
    def __init__(self, player, territory, target):
        Order.__init__(self, player, territory)
        Move.all_moves.append(self)
        self.target = target
        
    def resolve_bounce(self):
        if self.bounced:
            self.piece.challenging = self.piece.territory
            write_to_log("bounced piece at {0} is now challenging its own territory".format(self.piece.territory.name))
            self.bounced = False
        
    def create_bounces(self):
        challenging_pieces = self.piece.challenging.find_other_pieces_challenging_territory(self.piece)
        if not self.piece.has_most_strength(challenging_pieces) and challenging_pieces:
            self.bounced = True
    
    def target_accessible_by_convoy(self, territory):
        for piece in [piece for piece in Piece.all_pieces if piece.territory in territory.neighbours]:
            if piece in self.piece.convoyed_by and self.piece.convoyed_by[piece] == self.target:
                if self.territory_is_neighbour(piece.territory):
                    return True
                else: 
                    return self.target_accessible_by_convoy(neighbour)
        return False

    def move_is_valid(self):
        if not (self.target_accessible_by_convoy(self.territory) or self.territory_is_neighbour(self.target)):
            self.fail("move failed: {} is not a neighbour of {} and is not accessible by convoy".format(self.target.name, self.territory.name))
            return False
        if not (self.target.accessible_by_piece_type(self.piece)):
            self.fail("move failed: {} is not accessible by {} at {}".format(self.target.name, self.piece.piece_type, self.piece.territory.name))
            return False
        return  True

    def process_order(self):
        if self.move_is_valid():
            self.piece.challenging = self.target
            write_to_log("{} at {} is now challenging {}".format(self.piece.piece_type, self.territory.name, self.piece.challenging.name))
        else: 
            print(self.report)
        
    def __repr__(self):
        return "{}, {}: Move({}, {}, {})".format(self.year, self.phase, self.player, self.territory.name, self.target.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, move to {}.".format(self.year, self.phase, self.territory.name, self.player, self.target.name)
    
# Support -----------------------------------------------------------------------------------------
        
class Support(Order):
    def __init__(self, player, territory, supported_territory, target):
        Order.__init__(self, player, territory)
        self.target = target
        self.supported_territory = supported_territory
    
    def support_is_valid(self):
        
        if isinstance(self.target, Special_Coastal):
            return (self.territory_is_neighbour(self.target) and self.target.accessible_by_piece_type(self.piece)) or (self.territory_is_neighbour(self.target.parent_territory) and self.target.parent_territory.accessible_by_piece_type(self.piece))
            
        if isinstance(self.target, Special_Inland):
            for coast in self.target.coasts:
                if (self.territory_is_neighbour(self.target) and self.target.accessible_by_piece_type(self.piece)) or (self.territory_is_neighbour(self.target.coast) and self.target.coast.accessible_by_piece_type(self.piece)):
                    return True
            return False
        
        return self.territory_is_neighbour(self.target) and self.target.accessible_by_piece_type(self.piece)

    def process_order(self):
        if self.support_is_valid():
            object_piece = self.get_object_by_territory(self.supported_territory)
            
            if isinstance(self.target, Special_Coastal):
                if self.target in object_piece.strength:
                    object_piece.strength[self.target.parent_territory] +=1
                else:
                    object_piece.strength[self.target.parent_territory] = 1
                write_to_log("{} at {} is now supporting {} into {}".format(self.piece.piece_type, self.territory.name, object_piece.territory.name, self.target.parent_territory.name))
                write_to_log("{} at {} strength: {}".format(object_piece.piece_type, object_piece.territory.name, object_piece.strength))    
                
            
            else:
                if self.target in object_piece.strength:
                    object_piece.strength[self.target] +=1
                else:
                    object_piece.strength[self.target] = 1
                
                write_to_log("{} at {} is now supporting {} into {}".format(self.piece.piece_type, self.territory.name, object_piece.territory.name, self.target.name))
                write_to_log("{} at {} strength: {}".format(object_piece.piece_type, object_piece.territory.name, object_piece.strength))
            

        else:
            self.fail("support failed: {} at {} cannot support {} to {}".format(self.piece.piece_type, self.territory.name, self.supported_territory.name, self.target.name))
        
    def __repr__(self):
        return "{}, {}: Support({}, {}, {}, {})".format(self.year, self.phase, self.player, self.territory.name, self.supported_territory.name, self.target.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, support {} into {}.".format(self.year, self.phase, self.territory.name, self.player, self.supported_territory.name, self.target.name)
        

# Retreat --------------------------------------------------------------------------------------------
        
class Retreat(Order):
    def __init__(self, player, territory, target):
        Order.__init__(self, player, territory)
        self.target = target
        
    def retreat_is_valid(self):
        if not (self.territory_is_neighbour(self.target)):
            write_to_log("retreat failed: {} is not a neighbour of {}".format(self.target.name, self.territory.name))
            return False
        if not (self.target.accessible_by_piece_type(self.piece)):
            write_to_log("retreat failed: {} is not accessible by {} at {}".format(self.target.name, self.piece.piece_type, self.territory.name))
            return False
        if self.target == self.piece.find_other_piece_in_territory().previous_territory:
            write_to_log("retreat failed: {} at {} cannot retreat to the territory that the attacker came from.".format(self.piece.piece_type, self.territory.name))
            return False
        return  True
        
    def process_order(self):
        if self.retreat_is_valid():
            write_to_log("{} at {} has retreated to {}".format(self.piece.piece_type, self.territory.name, self.target.name))
            self.piece.territory = self.target
        else:
            self.piece.destroy()
        
    def __repr__(self):
        return "{}, {}: Retreat({}, {}, {})".format(self.year, self.phase, self.player, self.territory.name, self.target.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, retreat to {}.".format(self.year, self.phase, self.territory.name, self.player, self.target.name)
        
# Destroy -----------------------------------------------------------------------------------------

class Destroy(Order):
    def __init__(self, player, territory):
        Order.__init__(self, player, territory)
        
    def process_order(self):
        self.piece.destroy()
        
    def __repr__(self):
        return "{}, {}: Hold({}, {})".format(self.year, self.phase, self.player, self.territory)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, hold.".format(self.year, self.phase, self.territory.name, self.player)
        
# Build -------------------------------------------------------------------------------------------
        
class Build(Order):
    def __init__(self, player, piece_type, territory):
        Order.__init__(self, player, territory)
        self.piece_type = piece_type
        
    def process_order(self):
        if (not self.territory.occupied()) and self.territory.has_supply_center_which_belongs_to_player():
            if self.piece_type == "army":
                self.player.pieces.append(Army(self.territory, self.player))
                write_to_log("army built at {}".format(self.territory.name))
            if self.piece_type == "fleet" and isinstance(self.territory, Coastal):
                self.player.pieces.append(Fleet(self.territory, self.player))
                write_to_log("fleet built at {}".format(self.territory.name))
              
    def __repr__(self):
        return "{}, {}: Build({}, {}, {})".format(self.year, self.phase, self.player, self.piece_type, self.territory)
        
    def __str__(self):
        return "{}, {}: {} build {} at {}.".format(self.year, self.phase, self.player, self.piece_type, self.territory)
        
from piece import *