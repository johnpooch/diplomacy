from dependencies import *

# target has shared coast with origin
def territory_shares_coast_with_origin(origin, territory):
    for neighbour in territories[territory]["neighbours"]:
            if neighbour["name"] == origin:
                return neighbour["shared_coast"]
     
# target is accessible by piece_type --------------------------------------------------------------

def territory_is_accessible_by_piece_type(territory, piece):
    territory_type = territories[territory]["territory_type"]
    if piece["piece_type"] == "a":
        return territory_type != "water"
    else:
         # refactor
        return territory_type == "water" or (territory_type == "coastal" and territory_shares_coast_with_origin(piece["territory"], territory)) or (territory_type == "coastal" and territories[piece["territory"]]["territory_type"] == "water")
        
        
# territory is neighbour --------------------------------------------------------------------------

def territory_is_neighbour(origin, territory_to_check):
    neighbours = territories[origin]["neighbours"]
    if any(neighbour["name"] == territory_to_check for neighbour in neighbours):
        return True
    else:
        write_to_log("\tinvalid move. {0} is not a neighbour of {1}.".format(origin, territory_to_check))
        return False
        
        
# piece exists and_belongs to user ----------------------------------------------------------------

def piece_exists_and_belongs_to_user(order, pieces):
    for piece in pieces:
        if order["origin"] == piece["territory"] and order["nation"] == piece["owner"]:
            return piece
    write_to_log("\tinvalid move. there is no piece at this origin or it does not belong to the user.")
    return False