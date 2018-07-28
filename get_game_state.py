from dependencies import *
from objects import *

# GET GAME STATE ===================================================================================

def get_game_state():
    
    game_state = {
        "pieces" : [piece for piece in Piece.all_pieces],
        "game_properties": game_properties, 
    }
    return(game_state)