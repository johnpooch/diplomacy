# from dependencies import *
from nation import *
from phase import *
from game_properties import *
from piece import *
from territory import *
from order import *
from initial_game_state import *
from order_text_processor import get_orders_from_txt
from write_to_log import clear_log, clear_special

from territories import territories

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

def process_orders(turn):
    
    write_to_log("\n")
    get_orders_from_txt(turn)
    
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
        
    Move.all_moves =[]
    Order.all_orders =[]


# END TURN ========================================================================================

def end_turn(turn):
    process_orders(turn)

clear_log()