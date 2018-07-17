from dependencies import *
from process_helpers import *

def target_is__not_standoff(origin, target):
    return True

def target_is_not_attacker_origin(retreating_piece, pieces, target):
    # find_the_attacker piece
    for check_piece in pieces:
        if check_piece["territory"] == retreating_piece["territory"] and  check_piece["nation"] != retreating_piece["nation"]:
            attacker_piece = check_piece
        if attacker_piece["previous_territory"] == target:
            return False
    return True

# retreat is valid -----------------------------------------------------------------------------------
 
def retreat_is_valid(order, piece):
    return (territory_is_neighbour(order["origin"], order["target"])) and territory_is_accessible_by_piece_type(piece, order["target"] and target_is_not_attacker_origin(piece, get_pieces(), order["target"]) and target_is_not_standoff(order["origin"], order["target"]))
        
# process retreat ------------------------------------------------------------------------------------

def process_retreat(order, piece):
    if not retreat_is_valid(order, piece):
        write_to_log("invalid retreat")
        return False
    mongo.db.pieces.update_one({"territory": order["origin"]}, {"$set": {"territory": order["target"]}})
    return True