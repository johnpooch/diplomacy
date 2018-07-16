from dependencies import *

# GET GAME STATE ===================================================================================

def get_game_state():
    
    game_state = {
        "pieces" : [record for record in mongo.db.pieces.find()],
        "ownership": mongo.db.ownership.find_one(),
        "orders": [record for record in mongo.db.orders.find()],
        "game_properties": mongo.db.game_properties.find_one(),
        "users": [record for record in mongo.db.users.find()],
    }
    return(game_state)