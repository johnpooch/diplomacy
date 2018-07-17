from dependencies import *
from process_helpers import *
    
# update support --------------------------------------------------------------------------------

def update_support(order):
    object_supports = mongo.db.pieces.find_one({"territory": order["object"]})["support"]
    
    if order["target"] in object_supports:
        object_supports[order["target"]] +=1
        
    else:
        object_supports.update({order["target"]: 1})
        
    mongo.db.pieces.update({"territory": order["object"]}, {"$set":{"support": object_supports}})
        
# support is valid --------------------------------------------------------------------------------

def support_is_valid(order, piece):
    return territory_is_neighbour(order["origin"], order["target"]) and territory_is_accessible_by_piece_type(piece, order["target"])
    
# process support ---------------------------------------------------------------------------------

def process_support(order, piece):
    if support_is_valid(order, piece):
        update_support(order)
        return True
        
    return False
    