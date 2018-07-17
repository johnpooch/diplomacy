from dependencies import *
from process_helpers import *

# check for neighbour convoy ----------------------------------------------------------------------

def target_accessible_by_convoy(order, piece, origin):
    neighbours = territories[origin]["neighbours"]
    for neighbour in neighbours:
        if neighbour["name"] in piece["convoyed_by"] and neighbour["name"] != origin:
            if territory_is_neighbour(neighbour["name"], order["target"]):
                return True
            else: 
                return target_accessible_by_convoy(order, piece, neighbour["name"])
    return False

# move is valid -----------------------------------------------------------------------------------

def move_is_valid(order, piece):
    return (target_accessible_by_convoy(order, piece, order["origin"]) or territory_is_neighbour(order["origin"], order["target"])) and territory_is_accessible_by_piece_type(piece, order["target"])
        
# process move ------------------------------------------------------------------------------------

def process_move(order, piece):
    if not move_is_valid(order, piece):
        write_to_log("invalid move")
        return False
    mongo.db.pieces.update_one({"territory": order["origin"]}, {"$set": {"challenging": order["target"]}})
    return True