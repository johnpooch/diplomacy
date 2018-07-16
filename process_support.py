from dependencies import *
from process_helpers import *

# supported piece exists --------------------------------------------------------------------------

def supported_piece_exists(order, pieces):
    for piece in pieces:
        if order["object"] == piece["territory"]:
            return piece
    print("invalid move. there is no piece in this territory to support.")
    return False
    
# support is valid ----------------------------------------------------------------------------------
# REFACTOR? - could use same as move
def support_is_valid(order, pieces):
    piece = piece_exists_and_belongs_to_user(order, pieces)
    if not piece:
        print("invalid move. there is no piece at this origin or it does not belong to the user.")
        return False
    if not territory_is_neighbour(order["origin"], order["target"]):
        print("invalid move. target is not neighbour.")
        return False
    if not territory_is_accessible_by_piece_type(order["origin"], order["target"], piece):
        print("invalid move. target is not accessible.")
        return False
    if not supported_piece_exists(order, pieces):
        return False
    return True
    
# process support ------------------------------------------------------------------------------------

def process_support(order, pieces):
    if not support_is_valid(order, pieces):
        return False
    # check if support already exists
    object_supports = mongo.db.pieces.find_one({"territory": order["object"]})["support"]
    if order["target"] in object_supports:
        object_supports[order["target"]] +=1
    else:
        object_supports.update({order["target"]: 1})
    mongo.db.pieces.update({"territory": order["object"]}, {"$set":{"support": object_supports}})
    return True