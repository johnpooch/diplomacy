from process_orders import *

""" This script contians the functions that handle the end of a turn, i.e. when all order have been 
    submitted. """
    
# Clear db for next turn --------------------------------------------------------------------------

""" Clears order db and number of orders submitted for each user. Saves orders to roder_history db. """
# orders and order_history could be the same document in mongo db.

def clear_db_for_next_turn(mongo):
    for order in mongo.db.orders.find({}):
        mongo.db.order_history.insert(order)
    
    mongo.db.orders.remove({})
    mongo.db.users.update_many({}, {"$set" : { "orders_submitted" : 0 }})
    
# update num pieces -------------------------------------------------------------------------------
    
""" Updates number of pieces belonging to user in user db """
# this code feels unnecessary. the pieces should exist as a sub dictionary within the users doc.  
    
def update_num_pieces(mongo):
    mongo.db.users.update_many({}, { "$set": { "num_pieces" : 0 }})
    for piece in mongo.db.pieces.find({}):
        mongo.db.users.update({"nation" : piece["nation"]}, { "$inc" : { "num_pieces" : 1 }})
    
# update num orders spring ------------------------------------------------------------------------
    
""" Updates number orders that a user has after build phase. """
    
def update_num_orders_spring(mongo):
    for user in mongo.db.users.find({}):
        mongo.db.users.update({"_id" : user["_id"]}, { "$set" : { "num_orders" : user["num_pieces"] } })
    
# update num orders build -------------------------------------------------------------------------
    
""" Updates number orders that a user has during build phase based on the number of discrepancies. """
    
def update_num_orders_build(mongo):
    for user in mongo.db.users.find({}):
        if "piece_discrepancy" in user:
            mongo.db.users.update({"_id" : user["_id"]}, { "$set" : { "num_orders" : abs(user["piece_discrepancy"]) } })
        else:
            mongo.db.users.update({"_id" : user["_id"]}, { "$set" : { "num_orders" : 0 }})
    
# create discrepancies ----------------------------------------------------------------------------
    
""" Identifies discrepancies which exist between the number of pieces that a player ahs on the board and the 
    number of supply centers that the player owns. """
#  code feels unnecessarily complex.
    
def identify_discrepancies(mongo):
    mongo.db.users.update_many({}, {"$unset": { "piece_discrepancy" : 1 } })
    for user in mongo.db.users.find({}):
        piece_discrepancy = user["num_supply"] - user["num_pieces"]
        if piece_discrepancy != 0:
            mongo.db.users.update_one({"_id" : user["_id"]}, { "$set" : { "piece_discrepancy": piece_discrepancy } })
    

# Update user ownership db ------------------------------------------------------------------------

""" Update num_supply of users in mongo db after changes in ownership. """
# update_ownership_db and update_user_ownership_db could be handled using the same function. 
# This code feels unnecessarily complex. users and ownership dbs should be merged.

def update_user_ownership(mongo):
    mongo.db.users.update_many({}, { "$set" : { "num_supply": 0 } })
    for territory, owner in mongo.db.ownership.find_one({}).items():
        if owner != "neutral":
            mongo.db.users.update({ "nation" : owner }, { "$inc" : { "num_supply": 1 } })

# Update ownership db --------------------------------------------------------------------------------

""" Update mongo db with changes in ownership of territories. """
# update_ownership_db and update_user_ownership_db could be handled using the same function. 

def update_ownership_db(mongo, updated_ownerships):
    for updated_ownership in updated_ownerships:
        for nation in updated_ownership:
            mongo.db.ownership.update({}, {"$set" : { nation : updated_ownership[nation] }})
    
    
# Update pieces db --------------------------------------------------------------------------------

""" Updates pieces in the mongo db based on the positions of the piece objects. Handles the creation
    of new pieces in mongo. """
# code could be condensed. The use of ‘upsert’ could be explored.

def update_pieces_db(mongo, updated_pieces):
    for piece in updated_pieces:
        
        # if the piece does not have an id it is a piece that has just been built.
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
    
# Get valid orders --------------------------------------------------------------------------------

""" Return only orders which are valid for the current phase. """
# I think this code could be refactored if phases and orders were connected. 

def get_valid_orders(mongo):
    valid_orders = []
    if mongo.db.game_properties.find_one({})["phase"] in ["spring order phase", "fall order phase"]:
        for order in mongo.db.orders.find({}):
            if order["command"] in ["hold", "move", "support", "convoy"]:
                valid_orders.append(order)
    
    if mongo.db.game_properties.find_one({})["phase"] in ["spring retreat phase", "fall retreat phase"]:
        for order in mongo.db.orders.find({}):
            if order["command"] in ["retreat", "disband"]:
                valid_orders.append(order)
    
    if mongo.db.game_properties.find_one({})["phase"] == "fall build phase":
        for order in mongo.db.orders.find({}):
            if order["command"] in ["build", "disband"]:
                valid_orders.append(order)
    return valid_orders
    
# End turn ----------------------------------------------------------------------------------------

""" Orders that are not valid for the current game phase are excluded. Orders are processed. 
    Mongo db is updated with game state after orders are processed. """

def end_turn(mongo):
    
    orders_to_be_processed = get_valid_orders(mongo)

    # process orders
    updated_pieces, game_properties, updated_ownerships = process_orders(orders_to_be_processed, mongo.db.pieces.find({}), mongo.db.game_properties.find_one({}))
    
    # update pieces, ownership, game properties
    update_pieces_db(mongo, updated_pieces)
    update_ownership_db(mongo, updated_ownerships)
    mongo.db.game_properties.update({}, game_properties)
    
    # if the new phase is 'fall build phase', update user ownership and check how whether deficits or surpluses exist
    if mongo.db.game_properties.find_one({})["phase"] == "fall build phase":
        update_user_ownership(mongo)
        identify_discrepancies(mongo)
        update_num_orders_build(mongo)
        
        # skip the build phase if there are no surpluses or deficits
        if not any(["piece_discrepancy" in  user for user in mongo.db.users.find({})]):
            mongo.db.game_properties.update({}, { "year" : game_properties["year"] + 1, "phase" : "spring order phase" })
        
    # update number of pieces at start of new year. this doesn't account for units being disbanded.
    if mongo.db.game_properties.find_one({})["phase"] == "spring order phase":
        update_num_pieces(mongo)
        update_num_orders_spring(mongo)
    
    clear_db_for_next_turn(mongo)