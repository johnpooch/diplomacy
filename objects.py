from write_to_log import write_to_log

# IterRegistry ====================================================================================

""" this class allows iteration through instances of an object """
class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)

# Nation ==========================================================================================

class Nation():
    all_nations = []
    def __init__(self, name, pieces, num_supply_centres):
        Nation.all_nations.append(self)
        self.name = name
        self.pieces = pieces
        self.num_supply_centres = num_supply_centres
        self.orders_submitted = False
        self.surrendered = False
        
class Neutral():
    def __init__(self):
        self.name = "neutral"
        
# Phase ===========================================================================================

class Phase():
    def __init__(self):
        pass
    
# Fall Build Phase ------------------------------------------------------------------------------   

class Fall_Build_Phase(Phase):
    def __init__(self):
        self.name = "fall build phase"
    
    def end_phase(self):
        return Spring_Order_Phase()

# Retreat Phase -----------------------------------------------------------------------------------

class Retreat_Phase(Phase):
    def __init__(self):
        pass
    
# Fall Retreat Phase ------------------------------------------------------------------------------
    
class Fall_Retreat_Phase(Retreat_Phase):
    def __init__(self):
        self.name = "fall retreat phase"
    
    def end_phase(self):
        return Fall_Build_Phase()
    
# Spring Retreat Phase ----------------------------------------------------------------------------
    
class Spring_Retreat_Phase(Retreat_Phase):
    def __init__(self):
        self.name = "spring retreat phase"
    
    def end_phase(self):
        return Fall_Order_Phase()
    
# Order Phase -------------------------------------------------------------------------------------
    
class Order_Phase(Phase):
    def __init__(self):
        pass
    
# Fall Order Phase --------------------------------------------------------------------------------
    
class Fall_Order_Phase(Order_Phase):
    def __init__(self):
        self.name = "fall order phase"
    
    def end_phase(self):

        # update ownership of territories
        write_to_log("\n")
        for piece in Piece.all_pieces:
            if piece.territory.supply_center and  piece.territory.supply_center != piece.nation:
                write_to_log("supply center at {}, which belonged to {}, now belongs to {}".format(piece.territory.name, piece.territory.supply_center.name, piece.nation.name))
                setattr(piece.territory, "supply_center", piece.nation)
                
        if any([piece.retreat for piece in Piece.all_pieces]):
            return Fall_Retreat_Phase()
        else:
            return Fall_Build_Phase()
    
# Spring Order Phase ------------------------------------------------------------------------------
    
class Spring_Order_Phase(Order_Phase):
    def __init__(self):
        self.name = "spring order phase"
    
    def end_phase(self):
        if any([piece.retreat for piece in Piece.all_pieces]):
            return Spring_Retreat_Phase()
        else:
            return Fall_Order_Phase()

# Game Properties =================================================================================

class Game_Properties():
    def __init__(self):
        self.game_started = False
        self.phase = Spring_Order_Phase()
        self.year = 1901
        
    def end_phase(self):
        self.phase = self.phase.end_phase()
        write_to_log("\nnew phase: {}.".format(self.phase.name))
        if isinstance(self.phase, Spring_Order_Phase):
            setattr(game_properties, "year", self.year + 1)
            write_to_log("new year: {}.".format(self.year))
        
    def __repr__(self):
        
        return "{}, {}, {}".format(self.game_started, self.phase.name, self.year) 
        
    def __str__(self):
        return "Game Started: {}, Phase: {}, Year: {}".format(self.game_started, self.phase.name, self.year)
        
game_properties = Game_Properties()
        
# Territory =======================================================================================

class Territory():
    all_territories = []
    def __init__(self, name, display_name, neighbours):
        Territory.all_territories.append(self)
        self.name = name
        self.display_name = display_name
        self.neighbours = neighbours
        
    def occupied(self):
        return any([piece.territory == self for piece in Piece.all_pieces])
        
    def has_supply_center_which_belongs_to_player(self):
        return True
        
    def accessible_by_piece_type(self, piece):
        if isinstance(piece, Army):
            return not isinstance(self, (Water, Special_Coastal))
        if isinstance(piece, Fleet):
            # Refactor?
            return isinstance(self, Water) or (isinstance(self, Coastal) and self.shares_coast_with_piece(piece)) or (isinstance(self, Coastal) and isinstance(piece.territory, Water))

    def __repr__(self):
        return "{}, {}".format(self.name, self.display_name)
        
    def __str__(self):
        return "Name: {}, Display Name: {}".format(self.name, self.display_name)
        
# Water -------------------------------------------------------------------------------------------
        
class Water(Territory):
    def __init__(self, name, display_name, neighbours):
        Territory.__init__(self, name, display_name, neighbours)
        self.supply_center = False
        
# Coastal -----------------------------------------------------------------------------------------
        
class Coastal(Territory):
    def __init__(self, name, display_name, neighbours, shared_coasts, supply_center):
        Territory.__init__(self, name, display_name, neighbours)
        self.shared_coasts = shared_coasts
        self.supply_center = supply_center
        
    def shares_coast_with_piece(self, piece):
        return piece.territory in self.shared_coasts
        
# Inland ------------------------------------------------------------------------------------------
        
class Inland(Territory):
    def __init__(self, name, display_name, neighbours, supply_center):
        Territory.__init__(self, name, display_name, neighbours)
        self.supply_center = supply_center
        
# Special Inland ----------------------------------------------------------------------------------
        
class Special_Inland(Inland):
    def __init__(self, name, display_name, neighbours, supply_center, coasts):
        Inland.__init__(self, name, display_name, neighbours, supply_center)
        self.coasts = coasts
        
    def occupied(self):
        return any([piece.territory == self or self.coasts for piece in Piece.all_pieces])
        
# Special Coastal ---------------------------------------------------------------------------------
        
class Special_Coastal(Water):
    def __init__(self, name, display_name, neighbours, parent_territory):
        Water.__init__(self, name, display_name, neighbours)
        self.parent_territory = parent_territory
        
    def occupied(self):
        return any([piece.territory == self or self.parent_territory for piece in Piece.all_pieces])


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
        self.support = {}
        self.retreat = False
        
    def assign_piece_to_order(self):
        if self.order:
            self.order.piece = self
        
    def create_challenge(self):
        self.order.resolve_challenge()
        
    def has_most_support(self, challenging_pieces):
        for challenging_piece in challenging_pieces:
            # zero support
            if not self.challenging in challenging_piece.support:
                challenging_piece.support[self.challenging] = 0
            if not self.challenging in self.support:
                self.support[self.challenging] = 0
        return all(self.support[self.challenging] > challenging_piece.support[self.challenging] for challenging_piece in challenging_pieces)
        
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
        for neighbour in self.territory.neighbours:
            if (not neighbour.occupied()):
                print("neighbour of {} at {}, {} is not occupied".format(self.piece_type, self.territory.name, neighbour.name))
            if (neighbour.accessible_by_piece_type(self)):
                print("neighbour of {} at {}, {} is accessible".format(self.piece_type, self.territory.name, neighbour.name))
            if (neighbour == self.find_other_piece_in_territory().previous_territory):
                print("neighbour of {} at {}, {} is where the attacker came from".format(self.piece_type, self.territory.name, neighbour.name))
                
            # find previous territory of piece that is in piece's territory
            
                
        return any([neighbour for neighbour in self.territory.neighbours if (not neighbour.occupied()) and neighbour.accessible_by_piece_type(self) and neighbour != self.find_other_piece_in_territory().previous_territory])
        
    def must_retreat(self):
        self.retreat = True
        
    def retreat_resolved(self):
        self.retreat = False
    
    def destroy(self):
        Piece.all_pieces.remove(self)
        if self in Army.all_armies:
            Army.all_armies.remove(self)
        if self in Fleet.all_fleets:
            Fleet.all_fleets.remove(self)
            write_to_log("\npiece at {} has been destroyed".format(self.territory.name))
        
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
    
        
    def find_other_pieces_challenging_territory(self):
        return [piece for piece in Piece.all_pieces if piece.challenging == self.piece.challenging and id(self.piece) != id(piece)]
        
    def resolve_challenge(self):
        challenging_pieces = self.find_other_pieces_challenging_territory()
                
        if self.piece.has_most_support(challenging_pieces):
            for challenging_piece in challenging_pieces: 
                challenging_piece.challenging = challenging_piece.territory
                
        if challenging_pieces and not self.piece.has_most_support(challenging_pieces):
            self.piece.bounced = True
            write_to_log("piece at {0} challenging {1} has bounced".format(self.piece.territory.name, self.piece.challenging.name))
            self.piece.challenging = self.piece.territory
            write_to_log("bounced piece at {0} is now challenging its own territory".format(self.piece.territory.name))
                    
        if self.find_other_pieces_challenging_territory() != []:
            write_to_log("recursing the function because piece at {} is challenging {} the same territory as {}".format(piece["territory"], piece["challenging"], other_piece["territory"]))
            self.resolve_challenge()
        return True
        
    # Refactor?
    def identify_retreats(self):
        challenging_pieces = self.find_other_pieces_challenging_territory()
        if self.piece.has_most_support(challenging_pieces):
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
        challenging_pieces = self.find_other_pieces_challenging_territory()
        if not self.piece.has_most_support(challenging_pieces) and challenging_pieces:
            write_to_log("piece at {0} challenging {1} has bounced".format(self.piece.territory.name, self.piece.challenging.name))
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
            self.fail("move failed: {} is not accessible by piece type at {}".format(self.target.name, self.territory.name))
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
        return self.territory_is_neighbour(self.target) and self.target.accessible_by_piece_type(self.piece)

    def process_order(self):
        if self.support_is_valid():
            object_piece = self.get_object_by_territory(self.supported_territory)
            
            if self.target in object_piece.support:
                object_piece.support[self.target] +=1
            else:
                object_piece.support[self.target] = 1
        
    def __repr__(self):
        return "{}, {}: Support({}, {}, {}, {})".format(self.year, self.phase, self.player, self.territory.name, self.supported_territory.name, self.target.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, support {} into {}.".format(self.year, self.phase, self.territory.name, self.player, self.supported_territory.name, self.target.name)
        

# Retreat --------------------------------------------------------------------------------------------
        
class Retreat(Order):
    def __init__(self, player, territory, target):
        Order.__init__(self, player, territory)
        self.target = target
        
    def __repr__(self):
        return "{}, {}: Retreat({}, {}, {})".format(self.year, self.phase, self.player, self.territory.name, self.target.name)
        
    def __str__(self):
        return "{}, {}: piece at {}, belonging to {}, retreat to {}.".format(self.year, self.phase, self.territory.name, self.player, self.target.name)
        
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