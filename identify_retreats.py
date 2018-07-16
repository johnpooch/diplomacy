from dependencies import *
from get_pieces import get_pieces
from get_orders import get_orders

# identify retreats ------------------------------------------------------------------------------

def identify_retreats():
    # find pieces with matching territories
    for territory in territories:
        pieces_to_compare = mongo.db.pieces.find({"terrtitory": territory})
    return True