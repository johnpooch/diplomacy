# IMPORT AT BOTTOM OF SCRIPT CAN THIS BE FIXED?
    
def create_player(username):
    users = mongo.db.users
    
    nations = mongo.db.nations.find()
    for nation in nations:
        if nation["available"]:
            
            print(nation["name"])



def get_game_state():
    
    game_state = {
        "pieces" : [record for record in mongo.db.pieces.find()],
        "ownership": [record for record in mongo.db.ownership.find()],
        "orders": [record for record in mongo.db.orders.find()],
    }
    return(game_state)

import random
from game_state import game_state
from run import mongo