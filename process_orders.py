# from dependencies import *
from nation import *
from phase import *
from game_properties import *
from piece import *
from territory import *
from order import *
from initial_game_state import *
from order_text_processor import get_orders_from_txt
from write_to_log import clear_log

def find_territory_by_name(name):
    for territory in Territory.all_territories:
        if territory.name == name:
            return territory
            
def find_nation_by_name(name):
    for nation in Nation.all_nations:
        if nation.name == name:
            return nation

def piece_exists_in_territory_and_belongs_to_user(territory):
    for piece in Piece.all_pieces:
        if piece.territory == territory:
            return piece
            
def create_piece_objects(mongo_pieces):
    for piece in mongo_pieces:
        nation = find_nation_by_name(piece["nation"])
        territory = find_territory_by_name(piece["territory"])
        
        if piece["piece_type"] == "army":
            setattr(nation, "pieces", [Army(piece["_id"], territory, nation)])
            
        if piece["piece_type"] == "fleet":
            setattr(nation, "pieces", [Fleet(piece["_id"], territory, nation)])
            
def get_phase_by_string(string):
    # definitely bad code
    
    if string == "fall_build_phase":
        return Fall_Build_Phase()
    if string == "fall_retreat_phase":
        return Fall_Retreat_Phase()
    if string == "spring_retreat_phase":
        return Spring_Retreat_Phase()
    if string == "fall_order_phase":
        print("ay ay ay")
        return Fall_Order_Phase()
    if string == "spring_order_phase":
        return Spring_Order_Phase()
            
def assign_orders_to_pieces(mongo_orders):
    for order in mongo_orders:
        nation = order["nation"]  
        command = order["command"]
        origin = find_territory_by_name(order["territory"])
        
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
        if command == "destroy":
            order = Destroy(nation, origin)
        
        if command != "build":
            piece = piece_exists_in_territory_and_belongs_to_user(origin)
            if piece:
                setattr(piece, "order", order)
                
        else:
            Build(find_nation_by_name(nation), order["origin"], find_territory_by_name(order["target"]))

# Resolve Challenges ==================================================================================

def resolve_challenges():
    
    write_to_log("\n")
    for piece in Piece.all_pieces:
        piece.identify_retreats()
    
    write_to_log("\n")
    for move in Move.all_moves:
        move.create_bounces()
                
    write_to_log("\n")
    for move in Move.all_moves:
        move.resolve_bounce()
                
    write_to_log("\n")
    # REFACTOR
    for piece in Piece.all_pieces:
        for other_piece in Piece.all_pieces:
            if piece.challenging == other_piece.challenging and (not other_piece.retreat) and (not piece.retreat) and id(piece) != id(other_piece):
                write_to_log("recursing the function because piece at {} is challenging {} the same territory as {}".format(piece.territory.name, piece.challenging.name, other_piece.territory.name))
                resolve_challenges()
    return True

# Process Orders ==================================================================================

def process_orders(mongo_orders, mongo_pieces, mongo_game_properties):
    
    print(mongo_game_properties)

    game_properties = Game_Properties(mongo_game_properties["year"], get_phase_by_string(mongo_game_properties["phase"]))
    print(game_properties)
    clear_log()
    write_to_log("\n")

    # create piece object from mongo db piece
    create_piece_objects(mongo_pieces)
            
    # assign order to piece
    assign_orders_to_pieces(mongo_orders)
    
    for piece in Piece.all_pieces:
        piece.assign_piece_to_order()
    
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
            write_to_log("supply center at {}, which belonged to {}, now belongs to {}".format(piece.territory.name, piece.territory.supply_center.name, piece.nation.name))
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