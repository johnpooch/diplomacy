from territory import *
from game_properties import *

""" This script contains the order class and subclasses. """
# The order report property is not used effectively. 'Self.fail()' should be used on any unsuccessful order. 
# This could be displayed back to the user to show why an order did not succeed.

# Order ===========================================================================================

""" Parent class. All other orders inherit from this class. There are no instances of this class. """

class Order():
    all_orders = []
    
    def __init__(self, player, territory):
        Order.all_orders.append(self)
        self.player = player
        self.territory = territory
        self.year = Game_Properties.game_properties.year
        self.phase = Game_Properties.game_properties.phase
        self.success = True
        self.report = ""
        self.bounced = False
        self.piece = None
        print(Order.all_orders)
    
    def get_object_by_territory(self, territory):
        return [piece for piece in Piece.all_pieces if piece.territory.name == territory.name][0]

    def territory_is_neighbour(self, territory):
        neighbours = self.territory.neighbours
        return any(neighbour.name == territory.name for neighbour in neighbours)
            
    def fail(self, report_string):
        self.report = report_string
        self.success = False
        

# Hold --------------------------------------------------------------------------------------------

""" Hold. This class has no fucntionality in its process order mothed. This is because nothing needs to be processed in a hold order. """


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
        
""" Convoy. A convoy order expects object and target parameters. Object refers to the territory where the piece to be convoyed exists.
    Target refers to the territory where the object piece will attempt to move. All that needs to be determined for a valid convoy 
    move is that the piece is on water. The move associated with the convoy is what will fail if the convoy is ineffective. A valid 
    convoy order will be represented in the object piece by a dictionary in the piece's "convoyed_by" attribute. """
        
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
            if object_piece:
                object_piece.convoyed_by = {self.piece: self.target}
    
    def __repr__(self):
        return "{}, {}: Convoy({}, {}, {}, {})".format(self.year, self.phase, self.player, self.territory.name, self.convoyed_territory.name, self.target.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, convoy {} to {}.".format(self.year, self.phase, self.territory.name, self.player, self.convoyed_territory.name, self.target.name)
        
# Move --------------------------------------------------------------------------------------------

""" Move. A move order expects a target parameter which refers to the territory to which the piece will attempt to move. 
    A piece can successfully move to a territory if it is accessible by the piece type (i.e. army can't move to water territory)
    and the territory is a neighbour of the pieces current territory. A piece can also reach a territory if it is convoyed by fleets.
    
    A successful move causes the piece to be 'challenging the target territory'. """

class Move(Order):
    all_moves = []
    
    def __init__(self, player, territory, target):
        Order.__init__(self, player, territory)
        Move.all_moves.append(self)
        self.target = target
        
    def resolve_bounce(self):
        if self.bounced:
            self.piece.challenging = self.piece.territory
            self.bounced = False
        
    def create_bounces(self):
        challenging_pieces = self.piece.challenging.find_other_pieces_challenging_territory(self.piece)
        if not self.piece.has_most_strength(challenging_pieces) and challenging_pieces:
            self.bounced = True
    
    
    def target_accessible_by_convoy(self, territory):
        
        """ This function makes effective use of recursion. A chain of fleets can transport an army across multiple seas, ex. a chain of 
            fleets can transport an army from Edinburgh to Spain if the chain of fleets connects the two land propeties and all fleets
            are conoying the army to the target. This rule is represented in this recursive function. """
        
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
        
    def __repr__(self):
        return "{}, {}: Move({}, {})".format(self.year, self.phase, self.player, self.territory.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, move to .".format(self.year, self.phase, self.territory.name, self.player)
    
# Support -----------------------------------------------------------------------------------------
        
""" Support. A support order expects object and target parameters. Object refers to the territory where the piece to be supported exists.
    Target refers to the territory where the object piece will attempt to move. 
    
    A valid convoy order will be represented in the object piece by a dictionary in the piece's "strength" attribute. 
    
    Different conditions have to be satisfied when dealing with supporting a piece into a special coastal or special inland territory. """
        
# I think more concise code could be written to handle the special coast edge case with supports.
        
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
                    object_piece.strength[self.target.parent_territory] += 1
                else:
                    object_piece.strength[self.target.parent_territory] = 1
            
            else:
                if self.target in object_piece.strength:
                    object_piece.strength[self.target] +=1
                else:
                    object_piece.strength[self.target] = 1
        else:
            self.fail("support failed: {} at {} cannot support {} to {}".format(self.piece.piece_type, self.territory.name, self.supported_territory.name, self.target.name))
        
    def __repr__(self):
        return "{}, {}: Support({}, {}, {}, {})".format(self.year, self.phase, self.player, self.territory.name, self.supported_territory.name, self.target.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, support {} into {}.".format(self.year, self.phase, self.territory.name, self.player, self.supported_territory.name, self.target.name)


# Retreat --------------------------------------------------------------------------------------------
        
""" Retreat. Retreat funcitons similarly to move except that a piece cannot retreat to the territory from which the attacker came. If the 
    retreat fails, the piece is destroyed. """
        
class Retreat(Order):
    def __init__(self, player, territory, target):
        Order.__init__(self, player, territory)
        self.target = target
        
    def retreat_is_valid(self):
        if not (self.territory_is_neighbour(self.target)):
            self.fail("retreat failed: {} is not a neighbour of {}".format(self.target.name, self.territory.name))
            return False
        if not (self.target.accessible_by_piece_type(self.piece)):
            self.fail("retreat failed: {} is not accessible by {} at {}".format(self.target.name, self.piece.piece_type, self.territory.name))
            return False
        if self.target == self.piece.find_other_piece_in_territory().previous_territory:
            self.fail("retreat failed: {} at {} cannot retreat to the territory that the attacker came from.".format(self.piece.piece_type, self.territory.name))
            return False
        return  True
        
    def process_order(self):
        if self.retreat_is_valid():
            self.piece.territory = self.target
        else:
            self.piece.destroy()
        
    def __repr__(self):
        return "{}, {}: Retreat({}, {}, {})".format(self.year, self.phase, self.player, self.territory.name, self.target.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, retreat to {}.".format(self.year, self.phase, self.territory.name, self.player, self.target.name)
        
# Ddisband -----------------------------------------------------------------------------------------

""" Disband is an order that players can issue during retreat and build phases. It completely removes the piece. """

class Disband(Order):
    def __init__(self, player, territory):
        Order.__init__(self, player, territory)
        
    def process_order(self):
        self.piece.destroy()
        
    def __repr__(self):
        return "{}, {}: Hold({}, {})".format(self.year, self.phase, self.player, self.territory)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, hold.".format(self.year, self.phase, self.territory.name, self.player)
        
# Build -------------------------------------------------------------------------------------------
        
""" Build is an order that players can issue during build phases. It builds a new piece. Players must specify what type of piece
    they want to build. The territory in which to build the  piece must be unoccupied. """
    
# The rule whereby a player can only build a piece in a home territory is not represented.
        
class Build(Order):
    def __init__(self, player, piece_type, territory):
        Order.__init__(self, player, territory)
        self.piece_type = piece_type
        
    def process_order(self):
        if (not self.territory.occupied()) and self.territory.has_supply_center_which_belongs_to_player():
            if self.piece_type == "army":
                self.player.pieces.append(Army("", self.territory, self.player))
            if self.piece_type == "fleet" and isinstance(self.territory, Coastal):
                self.player.pieces.append(Fleet("", self.territory, self.player))
              
    def __repr__(self):
        return "{}, {}: Build({}, {})".format(self.year, self.phase.name, self.player.name, self.territory.name)
        
    def __str__(self):
        return "{}, {}: {} build at {}.".format(self.year, self.phase.name, self.player.name, self.territory.name)
        
from piece import *