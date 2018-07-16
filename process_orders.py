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

    for order in orders:
        if order["command"] == "convoy":
            write_to_log("{0} - processing order for piece at {1}: convoy {2} to {3}".format(order["nation"], order["origin"], order["object"], order["target"]))
            order["order_is_valid"] = process_convoy(order, get_pieces())
    for order in orders:
        if order["command"] == "move":
            write_to_log("{0} - processing order for piece at {1}: move to {2}".format(order["nation"], order["origin"], order["target"]))
            order["order_is_valid"] = process_move(order, get_pieces())
    for order in orders:
        if order["command"] == "support":
            write_to_log("{0} - processing order for piece at {1}: support {2} to {3}".format(order["nation"], order["origin"], order["object"], order["target"]))
            order["order_is_valid"] = process_support(order, get_pieces())
    write_to_log("\nall other orders are 'hold' orders")
    write_to_log("\norders")
            
    return True