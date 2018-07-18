from dependencies import *
from get_pieces import get_pieces

# territory shares coast with origin --------------------------------------------------------------

def territory_shares_coast_with_origin(origin, territory):
    for neighbour in territories[territory]["neighbours"]:
            if neighbour["name"] == origin:
                return neighbour["shared_coast"]
                
# territory is special coast --------------------------------------------------------------------

def territory_is_special_coast(territory):
    return "parent_territory" in territories[territory]
    
# territory has special coasts --------------------------------------------------------------------

def territory_has_special_coasts(territory):
    return "special_coasts" in territories[territory]
     
# target is accessible by piece_type --------------------------------------------------------------

def territory_is_accessible_by_piece_type(piece, territory):
    territory_type = territories[territory]["territory_type"]
    if piece["piece_type"] == "a":
        return territory_type != "water" or territory_is_special_coast(territory)
    else:
         # refactor
        return territory_type == "water" or (territory_type == "coastal" and territory_shares_coast_with_origin(piece["territory"], territory)) or (territory_type == "coastal" and territories[piece["territory"]]["territory_type"] == "water")
        
# territory is neighbour --------------------------------------------------------------------------

def territory_is_neighbour(origin, territory_to_check):
    
    if "bicoastal" in territories[origin]:
        print("FUCKer")
        for piece in get_pieces():
            if piece["territory"] == origin:
                piece = piece
                print("FUCK")
        neighbours = [neighbour for neighbour in territories[origin]["neighbours"] if neighbour["coast"] == piece["coast"]]
    else:
        neighbours = territories[origin]["neighbours"]
    # return true if the territory to check is one of its neighbours
    return any(neighbour["name"] == territory_to_check for neighbour in neighbours)
        
# object piece exists --------------------------------------------------------------------------

def object_piece_exists(order, pieces):
    for piece in pieces:
        if order["object"] == piece["territory"]:
            return True
    write_to_log("invalid move. there is no piece in this territory to support/convoy.")
    return False
        
# piece exists and_belongs to user ----------------------------------------------------------------

def piece_exists_and_belongs_to_user(order, pieces):
    for piece in pieces:
        if order["origin"] == piece["territory"] and order["nation"] == piece["owner"]:
            return piece
    write_to_log("\tinvalid move. there is no piece at {} or it does not belong to the user.".format(order["origin"]))
    return False