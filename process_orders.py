from dependencies import *
from process_helpers import *

from process_convoy import process_convoy
from process_move import process_move
from process_support import process_support

from get_pieces import get_pieces
from get_orders import get_orders

# UPDATE CHALLENGES ===============================================================================
    
# update challenges -------------------------------------------------------------------------------

def process_orders(orders):

    write_to_log("\nupdating challenges\n")

    # PUT ORDERS IN ARRAY IN CORRECT ORDER?

    for order in orders:
        if order["command"] == "convoy":
            write_to_log("{0} - processing order for piece at {1}: convoy {2} to {3}".format(order["nation"], order["origin"], order["object"], order["target"]))
            origin_piece = piece_exists_and_belongs_to_user(order, get_pieces())
            if object_piece_exists(order, get_pieces()) and origin_piece:
                order["order_is_valid"] = process_convoy(order, origin_piece)
                mongo.db.orders.update_one({"_id": order["_id"]}, {"$set": {"order_is_valid": order["order_is_valid"]}})
    for order in orders:
        if order["command"] == "move":
            write_to_log("{0} - processing order for piece at {1}: move to {2}".format(order["nation"], order["origin"], order["target"]))
            piece = piece_exists_and_belongs_to_user(order, get_pieces())
            if piece:
                order["order_is_valid"] = process_move(order, piece)
                mongo.db.orders.update_one({"_id": order["_id"]}, {"$set": {"order_is_valid": order["order_is_valid"]}})
    for order in orders:
        if order["command"] == "support":
            write_to_log("{0} - processing order for piece at {1}: support {2} to {3}".format(order["nation"], order["origin"], order["object"], order["target"]))
            origin_piece = piece_exists_and_belongs_to_user(order, get_pieces())
            if object_piece_exists(order, get_pieces()) and origin_piece:
                order["order_is_valid"] = process_support(order, origin_piece)
                mongo.db.orders.update_one({"_id": order["_id"]}, {"$set": {"order_is_valid": order["order_is_valid"]}})
    for order in orders:
        if order["command"] == "retreat":
            write_to_log("{0} - processing order for piece at {1}: retreat to {2}".format(order["nation"], order["origin"], order["target"]))
            if piece:
                order["order_is_valid"] = process_retreat(order, piece)
                mongo.db.orders.update_one({"_id": order["_id"]}, {"$set": {"order_is_valid": order["order_is_valid"]}})
                
    
    return True