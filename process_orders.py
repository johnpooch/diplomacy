from dependencies import *

from territories import territories


# CHANGE PLACES ===================================================================================

def change_places(orders):
    for order in orders:
        if order["order_is_valid"] and order["command"] == "move":
            piece = get_origin_by_order(order)
            mongo.db.pieces.update_one({
                        "_id": piece["_id"]
                    }, 
                    {
                        "$set": {"territory": piece["challenging"]}
                    })
    return True

# RESOLVE CHALLENGES ==============================================================================
    
# find other pieces challenging territory ---------------------------------------------------------
    
def find_other_pieces_challenging_territory(piece):
    print(piece["challenging"])
    territory = piece["challenging"]
    return [other_piece for other_piece in get_pieces() if other_piece["challenging"] == territory and piece["_id"] != other_piece["_id"]]

# does piece have most support --------------------------------------------------------------------

def piece_has_most_support(piece, pieces_to_compare):
    
    # zeroing support
    for other_piece in pieces_to_compare:
        if not piece["challenging"] in other_piece["support"]:
            other_piece["support"][piece["challenging"]] = 0
        if not piece["challenging"] in piece["support"]:
            piece["support"][piece["challenging"]] = 0
            
    return all(piece["support"][piece["challenging"]] > other_piece["support"][piece["challenging"]] for other_piece in pieces_to_compare)
    
# resolve challenges ------------------------------------------------------------------------------

def resolve_challenges(orders):
    
    """ this function needs to resolve challenges by determining if a piece has the most support into the territory its challenging.
    If the piece doesn't have the most support it should now be challenging the territory it came from. The process then needs to run recursively until all pieces are challenging the territory it came from. """
    
    for order in orders:
        if order["order_is_valid"] and order["command"] == "move":
            
            piece = get_origin_by_order(order)
            write_to_log("piece at {0} is challenging to {1}".format(piece["territory"], piece["challenging"]))
            
            pieces_to_compare = find_other_pieces_challenging_territory(piece)
            
            if not piece_has_most_support(piece, pieces_to_compare) and pieces_to_compare:
                
                write_to_log("piece at {0} challenging {1} has bounced".format(piece["territory"], piece["challenging"]))
                
                mongo.db.orders.update_one({
                    "_id": order["_id"]
                }, 
                {
                    "$set": {"bounced": True}
                })
                
    for order in get_orders():
        if order["bounced"]:
            piece = get_origin_by_order(order)
            mongo.db.pieces.update_one({
                    "_id": piece["_id"]
                }, 
                {
                    "$set": {"challenging": piece["territory"]}
                })
            write_to_log("bounced piece at {0} is now challenging its own territory".format(piece["territory"]))
                
                # CONFLICT
    for piece in get_pieces():
        for other_piece in get_pieces():
            if piece["challenging"] == other_piece["challenging"] and other_piece["_id"] != piece["_id"]:
                write_to_log("recursing the function because piece at {} is challenging {} the same territory as {}".format(piece["territory"], piece["challenging"], other_piece["territory"]))
                resolve_challenges(get_orders())
    return True

# =================================================================================================





# HELPERS =========================================================================================

# get_origin_by_order -----------------------------------------------------------------------------

def get_origin_by_order(order):
    for piece in get_pieces():
        if piece["_id"] == order["origin_id"]:
            return piece
    return False
    
# get_object_by_order -----------------------------------------------------------------------------

def get_object_by_order(order):
    for piece in get_pieces():
        if piece["_id"] == order["object_id"]:
            return piece
    return False

# territory shares coast with origin --------------------------------------------------------------

def territory_shares_coast_with_origin(origin, territory):
    for neighbour in territories[territory]["neighbours"]:
            if neighbour["name"] == origin:
                return neighbour["shared_coast"]
                
# territory is special coast --------------------------------------------------------------------

def territory_is_special_coast(territory):
    return "parent_territory" in territories[territory]
    
# territory has special coasts --------------------------------------------------------------------

def territory_has_special_coasts(territory):
    return "special_coasts" in territories[territory]
     
# target is accessible by piece_type --------------------------------------------------------------

def territory_is_accessible_by_piece_type(piece, territory):
    territory_type = territories[territory]["territory_type"]
    if piece["piece_type"] == "a":
        return territory_type != "water" or territory_is_special_coast(territory)
    else:
         # refactor
        return territory_type == "water" or (territory_type == "coastal" and territory_shares_coast_with_origin(piece["territory"], territory)) or (territory_type == "coastal" and territories[piece["territory"]]["territory_type"] == "water")
        
# territory is neighbour --------------------------------------------------------------------------

def territory_is_neighbour(origin, territory_to_check):
    
    neighbours = territories[origin]["neighbours"]
    # return true if the territory to check is one of its neighbours
    return any(neighbour["name"] == territory_to_check for neighbour in neighbours)
        
# object piece exists --------------------------------------------------------------------------

def object_piece_exists(order, pieces):
    for piece in pieces:
        if order["object"] == piece["territory"]:
            return piece["_id"]
    return False
        
# piece exists and_belongs to user ----------------------------------------------------------------

def piece_exists_and_belongs_to_user(order, pieces):
    for piece in pieces:
        if order["origin"] == piece["territory"] and order["nation"] == piece["owner"]:
            return piece["_id"]
    write_to_log("\tinvalid move. there is no piece at {} or it does not belong to the user.".format(order["origin"]))
    return False

# =================================================================================================





# PROCESS SUPPORT =================================================================================

# update support ----------------------------------------------------------------------------------

def update_support(order):
    object_piece = get_object_by_order(order)
    object_supports = mongo.db.pieces.find_one({"_id": object_piece["_id"]})["support"]
    
    if order["target"] in object_supports:
        object_supports[order["target"]] +=1
    else:
        object_supports.update({order["target"]: 1})
    mongo.db.pieces.update({"territory": order["object"]}, {"$set":{"support": object_supports}})
        
# support is valid --------------------------------------------------------------------------------

def support_is_valid(order):
    piece = get_origin_by_order(order)
    return territory_is_neighbour(order["origin"], order["target"]) and territory_is_accessible_by_piece_type(piece, order["target"])
    
# process support ---------------------------------------------------------------------------------

def process_support(order):
    if support_is_valid(order):
        update_support(order)
        return True
    return False
    
# get orders --------------------------------------------------------------------------------------

def get_orders():
    return [order for order in mongo.db.orders.find()]
    
# get pieces --------------------------------------------------------------------------------------
    
def get_pieces():
    return [piece for piece in mongo.db.pieces.find()]
    
# =================================================================================================






# PROCESS MOVE ====================================================================================

# target acceissible by convoy --------------------------------------------------------------------

def target_accessible_by_convoy(order, piece, origin):
    for neighbour in territories[origin]["neighbours"]:
        if neighbour["name"] in piece["convoyed_by"] and neighbour["name"] != origin:
            if territory_is_neighbour(neighbour["name"], order["target"]):
                return True
            else: 
                return target_accessible_by_convoy(order, piece, neighbour["name"])
    return False

# move is valid -----------------------------------------------------------------------------------

def move_is_valid(order):
    piece = get_origin_by_order(order)
    return (target_accessible_by_convoy(order, piece, order["origin"]) or territory_is_neighbour(order["origin"], order["target"])) and territory_is_accessible_by_piece_type(piece, order["target"])
        
# process move ------------------------------------------------------------------------------------

def process_move(order):
    if not move_is_valid(order):
        write_to_log("invalid move")
        return False
        
    mongo.db.pieces.update_one({"territory": order["origin"]}, {"$set": {"challenging": territories[order["target"]]["region"]}})
    return True

# =================================================================================================





# PROCESS CONVOY ==================================================================================

# piece is on water --------------------------------------------------------------------------------

def piece_is_on_water(piece):
    return territories[piece["territory"]]["territory_type"] == "water"
    
# process convoy ----------------------------------------------------------------------------------

def process_convoy(order):
    piece = get_origin_by_order(order)
    if piece_is_on_water(piece):
        mongo.db.pieces.update({"territory": order["object"]}, {"$push": {"convoyed_by": order["origin"]}})
        return True
    return False

# =================================================================================================






# UPDATE CHALLENGES ===============================================================================

def update_challenges(orders):
    
    for order in orders:
        if order["command"] == "convoy" and order["origin_id"] and order["object_id"]:
            order["order_is_valid"] = process_convoy(order)
            mongo.db.orders.update_one({"_id": order["_id"]}, {"$set": {"order_is_valid": order["order_is_valid"]}})
                
    for order in orders:
        if order["command"] == "move" and order["origin_id"]:
            order["order_is_valid"] = process_move(order)
            mongo.db.orders.update_one({"_id": order["_id"]}, {"$set": {"order_is_valid": order["order_is_valid"]}})
                
    for order in orders:
        if order["command"] == "support" and order["origin_id"] and order["object_id"]:
            order["order_is_valid"] = process_support(order)
            mongo.db.orders.update_one({"_id": order["_id"]}, {"$set": {"order_is_valid": order["order_is_valid"]}})
            
    for order in orders:
        if order["command"] == "retreat" and order["origin_id"]:
            order["order_is_valid"] = process_retreat(order, piece)
            mongo.db.orders.update_one({"_id": order["_id"]}, {"$set": {"order_is_valid": order["order_is_valid"]}})
        
    for order in orders:
        if order["command"] == "build":
            print("happy")
            
                
    return True
    
# =================================================================================================






# END TURN ========================================================================================

# save orders to history
def attach_pieces_to_order(orders, pieces):
    for order in orders:
        mongo.db.orders.update({"_id": order["_id"]}, {"$set": {"origin_id": piece_exists_and_belongs_to_user(order, pieces)}})
        mongo.db.orders.update({"_id": order["_id"]}, {"$set": {"object_id": object_piece_exists(order, pieces)}})

# save orders to history

def save_orders_to_history():
    order_history = mongo.db.order_history
    for order in get_orders():
        order_history.insert(order)

# check for retreats ------------------------------------------------------------------------------
def check_for_retreats():
    return any(piece["must_retreat"] for piece in get_pieces())
    
# check for builds --------------------------------------------------------------------------------
def check_for_builds():
    return True
    
# increment year ----------------------------------------------------------------------------------

def increment_year():
    new_year = (mongo.db.game_properties.find_one()["year"] + 1)
    write_to_log("year incremented. new year: {}".format(new_year))
    mongo.db.game_properties.update({}, {"$set": {"year": new_year}})

# change phase ------------------------------------------------------------------------------

def change_phase(current_phase):
    
    # if spring moves
    if current_phase == 0:
        if check_for_retreats():
            update_phase = 1
        else: 
            update_phase = 2
            
    # if spring retreats
    if current_phase == 1:
        update_phase = 2
            
    # if fall moves
    if current_phase == 2:
        if check_for_retreats():
            update_phase = 3
        elif check_for_builds():
            update_phase = 4
            
    # if fall retreats
    if current_phase == 3:
        if check_for_builds:
            update_phase = 4
        else: 
            update_phase = 0
        
    # if fall retreats
    if current_phase == 4:
        increment_year()
        update_phase = 0
        
    write_to_log("\nphase updated from {0} to {1}.".format(current_phase, update_phase))
    mongo.db.game_properties.update_one({}, {"$set": {"phase": update_phase}})
    
# unfinalise_users --------------------------------------------------------------------------------

def unfinalise_users():
    mongo.db.users.update({}, {"$set": {"orders_finalised": False}}, multi=True)
    write_to_log("user orders unfinalised\n")
    
# write to log ------------------------------------------------------------------------------------
    
def write_to_log(string):
    with open('log.txt', 'a') as log:
        log.write(string + '\n')
        
# clear log ---------------------------------------------------------------------------------------
        
def clear_log():
    open('log.txt', 'w').close()

# end turn ----------------------------------------------------------------------------------------

def end_turn():
    
    clear_log()
    unfinalise_users()
    
    attach_pieces_to_order(get_orders(), get_pieces())
    update_challenges(get_orders())
    resolve_challenges(get_orders())
    
    change_places(get_orders())

    change_phase(mongo.db.game_properties.find_one({})["phase"])
    
    # remove_all_support()
    save_orders_to_history()
    # mongo.db.orders.remove({})
    flash('Orders proccessed!', 'success')
