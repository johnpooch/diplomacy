from flask import request
from order import *

# CREATE ORDER ====================================================================================
    
# piece exists and belongs to user ---------------------------------------------------------------------------

""" Find out if a piece belonging to the user exists in the 'territory' of an order. """

def piece_exists_and_belongs_to_player(order, pieces):
    for piece in pieces:
        if order["origin"] == piece["territory"] and order["nation"] == piece["owner"]:
            return piece["_id"]
    return False
    
# Create Order ------------------------------------------------------------------------------------
    
""" Instances of order objects are created and attached to the piece located at the order 'territory'. This code feels
    repetitive and I think it could be refactored to look cleaner. """
    
def create_order(request, piece):
    
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
        if command == "disband":
            piece.order = Disband(nation, territory, target)
        
    else:
        return False