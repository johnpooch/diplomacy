from dependencies import *
from order import *


# CREATE ORDER ====================================================================================
    
# Filter pieces by user ---------------------------------------------------------------------------
    
def filter_pieces_by_user(username):
    user = mongo.db.users.find_one({"username": username})
    pieces = mongo.db.pieces.find()
    return [piece for piece in pieces if piece["owner"] == user["nation"]]
    
# piece exists and belongs to user ---------------------------------------------------------------------------

def piece_exists_and_belongs_to_player(order, pieces):
    for piece in pieces:
        if order["origin"] == piece["territory"] and order["nation"] == piece["owner"]:
            return piece["_id"]
    write_to_log("\tinvalid move. there is no piece at {} or it does not belong to the user.".format(order["origin"]))
    return False
    
# Create Order ------------------------------------------------------------------------------------
    
def create_order(request, piece, game_state, username):
    
    territory = request.form[(piece["territory"] + "-origin")],
    command = request.form[(piece["territory"] + "-command")],
    target = request.form[(piece["territory"] + "-target")],
    _object = request.form[(piece["territory"] + "-object")],
    nation = request.form["player"]
    
    piece = piece_exists_and_belongs_to_player(territory, nation)
    
    if piece:
        if command == "hold":
            piece.order = Hold(nation, territory)
        if command == "move":
            piece.order = Move(nation, territory, target)
        if command == "support":
            piece.order = Support(nation, territory, _object, target)
        if command == "convoy":
            piece.order = Convoy(nation, territory, _object, target)
        if command == "retreat":
            piece.order = Retreat(nation, territory, target)
        if command == "build":
            piece.order = Retreat(nation, territory, piece_type)
        
    else:
        return False