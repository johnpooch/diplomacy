from dependencies import *

# CREATE ORDER ====================================================================================
    
# Filter pieces by user ---------------------------------------------------------------------------
    
def filter_pieces_by_user(username):
    user = mongo.db.users.find_one({"username": username})
    pieces = mongo.db.pieces.find()
    return [piece for piece in pieces if piece["owner"] == user["nation"]]
    
# Upload order to DB ------------------------------------------------------------------------------
    
def upload_order_to_db(request, pieces, game_state, username):
    for piece in pieces:
        order = {
            "origin": request.form[(piece["territory"] + "-origin")],
            "command": request.form[(piece["territory"] + "-command")],
            "target": request.form[(piece["territory"] + "-target")],
            "object": request.form[(piece["territory"] + "-object")],
            "year": game_state["game_properties"]["year"],
            "phase": game_state["game_properties"]["phase"],
            "nation": mongo.db.users.find_one({"username": username})["nation"]
        }
        mongo.db.orders.insert(order)
        mongo.db.users.update_one({"username": username}, {"$set": {"orders_finalised": True}})
    flash('Orders finalised!', 'success')