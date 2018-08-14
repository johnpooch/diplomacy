import random
from flask import request, flash

# Create player -----------------------------------------------------------------------------------
    
def create_player(mongo, request):
    
    nation = random.choice([nation for nation in mongo.db.nations.find({"available": True})])
    mongo.db.nations.update_one({'_id': nation['_id']}, { '$set': {'available': False}})
    
    player_nation = nation['name']
    if player_nation == "russia":
        num_supply = 4
    else:
        num_supply = 3
    
    mongo.db.users.insert(
        {
        "username": request.form["username"],
        "email": request.form["email"],
        "password": request.form["password"],
        "nation": player_nation,
        "orders_submitted": 0,
        "num_supply": num_supply,
        "num_pieces": num_supply, 
        "num_orders": num_supply,
        "orders_finalised": False
        }
    )
    flash('Account created for {}!'.format(request.form["username"]), 'success')
    return request.form["username"]