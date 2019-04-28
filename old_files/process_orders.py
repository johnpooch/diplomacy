# from dependencies import *
from nation import *
from phase import *
from game_properties import *
from piece import *
from territory import *
from order import *
from initial_game_state import *
from order_text_processor import get_orders_from_txt

# find territory by name ==========================================================================

""" returns instance of territory object from string. """

def find_territory_by_name(name):
    for territory in Territory.all_territories:
        if territory.name == name:
            return territory
            
# find nation by name =============================================================================

""" returns instance of nation object by given string  """
            
def find_nation_by_name(name):
    for nation in Nation.all_nations:
        if nation.name == name:
            return nation
            
# get phase by string =============================================================================
            
""" returns instance of phase object from string. """
# definitely bad code. could be done more elegantly using the 'name' attribute of each phase. Would need list of phases.
            
def get_phase_by_string(string):
    
    if string == "fall build phase":
        return Fall_Build_Phase()
    if string == "fall retreat phase":
        return Fall_Retreat_Phase()
    if string == "spring retreat phase":
        return Spring_Retreat_Phase()
    if string == "fall order phase":
        return Fall_Order_Phase()
    if string == "spring order phase":
        return Spring_Order_Phase()
            
# piece exists in territory and belongs to user ===================================================

""" returns piece if a piece exists in a territory and belongs to the given nation. """

def piece_exists_in_territory_and_belongs_to_user(territory, user_nation):
    for piece in Piece.all_pieces:
        if piece.territory == territory and piece.nation.name == user_nation:
            return piece
            
# create piece objects ============================================================================

""" turns mongo db pieces into instances of piece objects. """
            
def create_piece_objects(mongo_pieces):
    for piece in mongo_pieces:
        nation = find_nation_by_name(piece["nation"])
        territory = find_territory_by_name(piece["territory"])
        
        if piece["piece_type"] == "army":
            setattr(nation, "pieces", [Army(piece["_id"], territory, nation)])
            
        if piece["piece_type"] == "fleet":
            setattr(nation, "pieces", [Fleet(piece["_id"], territory, nation)])
            
# assign orders to pieces =========================================================================

""" Creates instance of order using mongo db data and assigns the order to the piece. """

# This code is too repetitive. If orders had a 'name' attribute, this code could be done more elegantly. 
            
def assign_orders_to_pieces(mongo_orders):
    for order in mongo_orders:
        nation = order["nation"]  
        piece_type = order["piece_type"]
        command = order["command"]
        origin = find_territory_by_name(order["territory"])
        
        if command != "build":
            piece = piece_exists_in_territory_and_belongs_to_user(origin, nation)
            if piece:
                
                if command == "hold":
                    order = Hold(nation, origin)
                if command == "convoy":
                    order = Convoy(nation, origin, find_territory_by_name(order["object"]), find_territory_by_name(order["target"]))
                if command == "move":
                    order = Move(nation, origin, find_territory_by_name(order["target"]))
                if command == "support":
                    # need to account for army ven support nap to hold!
                    order = Support(nation, origin, find_territory_by_name(order["object"]), find_territory_by_name(order["target"]))
                if command == "retreat":
                    order = Retreat(nation, origin, find_territory_by_name(order["target"]))
                if command == "disband":
                    order = Disband(nation, origin)
                setattr(piece, "order", order)
        else:
            Build(find_nation_by_name(nation), piece_type, find_territory_by_name(order["territory"]))
            for order in Order.all_orders:
                print(order)

# Resolve Challenges ==================================================================================

""" The challenges that are created from move and retreat orders are resolved. When a pice challenges a territory and is bounced, the 
    piece is now challenging the territory where it came from. This means that any piece which is challenging the origin location of
    another piece which is bounced should cause another bounce.
    
    For example: army gre move bul, army con move bul, army smy move con. --> all three pieces should bounce.
    
    This function uses recursion to represent this issue. """
    
# code feels a little repetitive. 

def resolve_challenges():
    
    for piece in Piece.all_pieces:
        piece.identify_retreats()
    
    for move in Move.all_moves:
        move.create_bounces()
                
    for move in Move.all_moves:
        move.resolve_bounce()
                
    for piece in Piece.all_pieces:
        for other_piece in Piece.all_pieces:
            if piece.challenging == other_piece.challenging and (not other_piece.retreat) and (not piece.retreat) and id(piece) != id(other_piece):
                resolve_challenges()
    return True


# Process Orders ==================================================================================

""" Converts mongo db data into instances of objects. Assigns order to piece and vice versa. Runs the process_order method of 
    each piece. Resolves challenges created by move orders. Restores conditions after orders have been processed. Ends phase.
    
    Convoy orders have to be carried out first because the validity of a move order is dependent on convoy orders. """ 
    
# This function should be decomposed into smaller pieces. The function serves too many purposes.

def process_orders(mongo_orders, mongo_pieces, mongo_game_properties):
    
    # convert mongo db data into class instances
    game_properties = Game_Properties(mongo_game_properties["year"], get_phase_by_string(mongo_game_properties["phase"]))
    create_piece_objects(mongo_pieces)
    assign_orders_to_pieces(mongo_orders)
    for piece in Piece.all_pieces:
        piece.assign_piece_to_order()
    
    # process orders
    for order in Order.all_orders:
    # convoy orders have to be carried out before other orders
        if isinstance(order, Convoy):
            order.process_order()
    for order in Order.all_orders:
        if not isinstance(order, Convoy):
            order.process_order()
        
    if isinstance(game_properties.phase, Order_Phase):
        resolve_challenges()
        for move in Move.all_orders:
            move.piece.change_territory()
        for piece in Piece.all_pieces:
            if piece.retreat and not piece.can_retreat():
                piece.destroy()
    
    # remove all supports
    for piece in Piece.all_pieces:
        setattr(piece, "support", {})
        
    # change phase
    game_properties.end_phase()
    
    # delete orders
    Move.all_moves = []
    Order.all_orders = []
    
    piece_list = []
    for piece in Piece.all_pieces:
        piece_list.append({
            "territory": piece.territory.name, 
            "nation": piece.nation.name, 
            "piece_type": piece.piece_type, 
            "previous_territory": piece.previous_territory.name,
            "retreat": piece.retreat,
            "_id": piece.mongo_id
        })
        
    # update ownership of territories
    updated_ownership = []
    for piece in Piece.all_pieces:
        if piece.territory.supply_center and  piece.territory.supply_center != piece.nation:
            updated_ownership.append({piece.territory.name: piece.nation.name})
        
    Piece.all_pieces = []
    
    # check if this is necessary
    Army.all_armies = []
    Fleet.all_fleets = []
  
    return_game_properties = {
        "phase": game_properties.phase.name, 
        "year": game_properties.year,
    }
        
    return piece_list, return_game_properties, updated_ownership