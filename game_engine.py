# IMPORT AT BOTTOM OF SCRIPT CAN THIS BE FIXED?
from flask import abort, Response
    
    
def update_nation_availability(player_nation):
    nation_to_update = mongo.db.nations.find_one({'name': player_nation})
    update_doc={"available": False}
    mongo.db.nations.update_one(nation_to_update, {'$set': update_doc})
    
def create_player(username):
    
    nations = mongo.db.nations.find()
    for nation in nations:
        if nation["available"]:
            player_nation = nation["name"]
            break

    if not player_nation:
        abort(Response('Something has gone worng. Nation not assigned.'))
        
    update_nation_availability(player_nation)
    return player_nation

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