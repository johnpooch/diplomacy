from dependencies import *
from process_helpers import *

# piece is on water --------------------------------------------------------------------------------

def piece_is_on_water(piece):
    if territories[piece["territory"]]["territory_type"] == "water":
        return True
    write_to_log("{}: invalid move. piece must be on water to convoy.".format(piece["territory"]))
    return False
    
# process convoy ----------------------------------------------------------------------------------

def process_convoy(order, piece):
    if piece_is_on_water(piece):
        mongo.db.pieces.update({"territory": order["object"]}, {"$push": {"convoyed_by": order["origin"]}})
        return True
    else:
        return False