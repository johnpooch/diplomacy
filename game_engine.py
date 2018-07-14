# IMPORT AT BOTTOM OF SCRIPT CAN THIS BE FIXED?
from flask import abort, Response
    
    



def get_game_state():
    
    game_state = {
        "pieces" : [record for record in mongo.db.pieces.find()],
        "ownership": mongo.db.ownership.find_one(),
        "orders": [record for record in mongo.db.orders.find()],
        "game_properties": mongo.db.game_properties.find_one(),
    }
    return(game_state)

import random
from game_state import game_state
from run import mongo