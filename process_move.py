from dependencies import *
from process_helpers import *

# check for neighbour convoy ----------------------------------------------------------------------

def check_for_neighbour_convoy(order, piece, origin):
    neighbours = territories[origin]["neighbours"]
    for neighbour in neighbours:
        if neighbour["name"] in piece["convoyed_by"] and neighbour["name"] != origin:
            if territory_is_neighbour(neighbour["name"], order["target"]):
                return True
            else: 
                check_for_neighbour_convoy(order, piece, neighbour["name"])
    return False

# target accessible by convoy ---------------------------------------------------------------------

def target_accessible_by_convoy(order, piece):
    return check_for_neighbour_convoy(order, piece, order["origin"])

# move is valid -----------------------------------------------------------------------------------

def move_is_valid(order, pieces):
    piece = piece_exists_and_belongs_to_user(order, pieces)
    if not piece:
        print("invalid move. there is no piece at this origin or it does not belong to the user.")
        return False
    return (target_accessible_by_convoy(order, piece) or territory_is_neighbour(order["origin"], order["target"])) and territory_is_accessible_by_piece_type(piece, territory)
        
# process move ------------------------------------------------------------------------------------

def process_move(order, pieces):
    if not move_is_valid(order, pieces):
        return False
    mongo.db.pieces.update_one({"territory": order["origin"]}, {"$set": {"challenging": order["target"]}})
    return True