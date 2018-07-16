from dependencies import *
from process_helpers import *

# convoyed piece exists --------------------------------------------------------------------------

def convoyed_piece_exists(order, pieces):
    for piece in pieces:
        if order["object"] == piece["territory"]:
            return True
    print("invalid move. there is no piece in this territory to support.")
    return False
    
# piece is on water --------------------------------------------------------------------------------

def piece_is_on_water(order):
    if territories[order["origin"]]["territory_type"] == "water":
        return True
    print("{}: invalid move. piece must be on water to convoy.".format(order["origin"]))
    return False
    
# convoy is valid ----------------------------------------------------------------------------------

def convoy_is_valid(order, pieces):
    return piece_exists_and_belongs_to_user(order, pieces) and convoyed_piece_exists(order, pieces) and piece_is_on_water(order)
    
# process convoy ----------------------------------------------------------------------------------

def process_convoy(order, pieces):
    if not convoy_is_valid(order, pieces):
        return False
    print("CONVOY SUCCESSFUL: ".format)
    mongo.db.pieces.update({"territory": order["object"]}, {"$push": {"convoyed_by": order["origin"]}})
    return True