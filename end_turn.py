from process_orders import *
    
# Clear db for next turn --------------------------------------------------------------------------

def clear_db_for_next_turn(mongo):
    
    for order in mongo.db.orders.find({}):
        mongo.db.order_history.insert(order)
    
    mongo.db.orders.remove({})
    mongo.db.users.update_many({}, {"$set" : { "orders_submitted" : 0 }})
    
# update num pieces -------------------------------------------------------------------------------
    
def update_num_pieces(mongo):
    mongo.db.users.update_many({}, { "$set": { "num_pieces" : 0 }})
    for piece in mongo.db.pieces.find({}):
        mongo.db.users.update({"nation" : piece["nation"]}, { "$inc" : { "num_pieces" : 1 }})
    
# update num orders spring ------------------------------------------------------------------------
    
def update_num_orders_spring(mongo):
    for user in mongo.db.users.find({}):
        mongo.db.users.update({"_id" : user["_id"]}, { "$set" : { "num_orders" : user["num_pieces"] } })
    
# update num orders build -------------------------------------------------------------------------
    
def update_num_orders_build(mongo):
    for user in mongo.db.users.find({}):
        if "piece_discrepancy" in user:
            mongo.db.users.update({"_id" : user["_id"]}, { "$set" : { "num_orders" : abs(user["piece_discrepancy"]) } })
        else:
            mongo.db.users.update({"_id" : user["_id"]}, { "$set" : { "num_orders" : 0 }})
    
# create_discrepancies ----------------------------------------------------------------------------
    
def create_discrepancies(mongo):
    mongo.db.users.update_many({}, {"$unset": { "piece_discrepancy" : 1 } })
    for user in mongo.db.users.find({}):
        piece_discrepancy = user["num_supply"] - user["num_pieces"]
        if piece_discrepancy != 0:
            mongo.db.users.update_one({"_id" : user["_id"]}, { "$set" : { "piece_discrepancy": piece_discrepancy } })
    

# Update user ownership db --------------------------------------------------------------------------------

def update_user_ownership(mongo):
    mongo.db.users.update_many({}, { "$set" : { "num_supply": 0 } })
    for territory, owner in mongo.db.ownership.find_one({}).items():
        if owner != "neutral":
            mongo.db.users.update({ "nation" : owner }, { "$inc" : { "num_supply": 1 } })

# Update ownership db --------------------------------------------------------------------------------

def update_ownership_db(mongo, updated_ownership_list):
    print("yo")
    for updated_ownership in updated_ownership_list:
        for nation in updated_ownership:
            mongo.db.ownership.update({}, {"$set" : { nation : updated_ownership[nation] }})
    return True
    
    
# Update pieces db --------------------------------------------------------------------------------

def update_pieces_db(mongo, updated_pieces):
    for piece in updated_pieces:
        if piece["_id"] == "":
            mongo.db.pieces.insert(
                {
                "nation": piece["nation"], 
                "piece_type": piece["piece_type"],
                "territory": piece["territory"], 
                "previous_territory": piece["previous_territory"], 
                "retreat": piece["retreat"], 
                })
        else: 
            mongo.db.pieces.update({"_id": piece["_id"]}, 
            {
                "nation": piece["nation"], 
                "piece_type": piece["piece_type"],
                "territory": piece["territory"], 
                "previous_territory": piece["previous_territory"], 
                "retreat": piece["retreat"], 
            })
    return True
    
# End turn ----------------------------------------------------------------------------------------

def end_turn(mongo):
    
    orders_to_be_processed = []
    
    if mongo.db.game_properties.find_one({})["phase"] in ["spring order phase", "fall order phase"]:
        for order in mongo.db.orders.find({}):
            if order["command"] in ["hold", "move", "support", "convoy"]:
                orders_to_be_processed.append(order)
    
    if mongo.db.game_properties.find_one({})["phase"] in ["spring retreat phase", "fall retreat phase"]:
        for order in mongo.db.orders.find({}):
            if order["command"] in ["retreat", "disband"]:
                orders_to_be_processed.append(order)
    
    if mongo.db.game_properties.find_one({})["phase"] == "fall build phase":
        for order in mongo.db.orders.find({}):
            if order["command"] in ["build", "disband"]:
                orders_to_be_processed.append(order)
        
    print("ORDERS TO BE PROCESSED: {}".format(orders_to_be_processed))
    
    updated_pieces, game_properties, updated_ownership = process_orders(orders_to_be_processed, mongo.db.pieces.find({}), mongo.db.game_properties.find_one({}))
    update_pieces_db(mongo, updated_pieces)
    update_ownership_db(mongo, updated_ownership)
    mongo.db.game_properties.update({}, game_properties)
    
    print("PHASE: {}".format(mongo.db.game_properties.find_one({})["phase"]))
    
    if mongo.db.game_properties.find_one({})["phase"] == "fall build phase":
        update_user_ownership(mongo)
        create_discrepancies(mongo)
        update_num_orders_build(mongo)
        
        if not any(["piece_discrepancy" in  user for user in mongo.db.users.find({})]):
            mongo.db.game_properties.update({}, { "year" : game_properties["year"] + 1, "phase" : "spring order phase" })
        
        
    if mongo.db.game_properties.find_one({})["phase"] == "spring order phase":
        update_num_pieces(mongo)
        update_num_orders_spring(mongo)
    
    clear_db_for_next_turn(mongo)