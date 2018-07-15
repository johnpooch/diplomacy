# IMPORT AT BOTTOM OF SCRIPT CAN THIS BE FIXED?

from players import dummy_players
from initial_game_state import *
    
# SETUP ===========================================================================================

# Clear DB --------------------------------------

def clear_db():
    mongo.db.pieces.remove({})
    mongo.db.users.remove({})
    mongo.db.ownership.remove({})
    mongo.db.orders.remove({})
    mongo.db.nations.remove({})
    mongo.db.game_properties.remove({})
    
# Initialise game DB ----------------------------

def initialise_game_db():
    clear_db()
    pieces = mongo.db.pieces
    for piece in initial_pieces:
        pieces.insert(piece)
    nations = mongo.db.nations
    for nation in initial_nations:
        nations.insert(nation)
    mongo.db.ownership.insert(initial_ownership)
    mongo.db.game_properties.insert(initial_game_properties)
    flash('Game initialised!', 'success')
    
# Populate Users --------------------------------

""" creates seven dummy users """

def populate_users():
    mongo.db.users.remove({})
    users = mongo.db.users
    for player in dummy_players:
        users.insert(player)
        
# Fill out orders -------------------------------

""" creates a list of pre-written orders """
        
def fill_out_orders():
    mongo.db.orders.remove({})
    orders = mongo.db.orders
    for order in initial_orders:
        orders.insert(order)
        
# Are seven players registered ------------------

def are_seven_players_registered():
    return mongo.db.users.count() >= 7
        
# Update nation availability --------------------
    
def update_nation_availability(player_nation):
    nation_to_update = mongo.db.nations.find_one({'name': player_nation})
    update_doc={"available": False}
    mongo.db.nations.update_one(nation_to_update, {'$set': update_doc})
    
# Assign player to nation -----------------------

def assign_player_to_nation(username):
    nations = mongo.db.nations.find()
    for nation in nations:
        if nation["available"]:
            player_nation = nation["name"]
            break
    if not player_nation:
        abort(Response('Something has gone wrong. Nation not assigned.'))
    update_nation_availability(player_nation)
    return player_nation
    
# Create player ---------------------------------
    
def create_player(request):
    mongo.db.users.insert(
        {
        "username": request.form["username"],
        "email": request.form["email"],
        "password": bcrypt.hashpw(request.form["password"].encode('utf-8'), bcrypt.gensalt()),
        "nation": assign_player_to_nation(request.form["username"]),
        "orders_finalised": False
        }
    )
    flash('Account created for {}!'.format(request.form.username.data), 'success')
    return request.form["username"]
    
    
# Attempt login ------------------------------------

def attempt_login(request):

    user_to_compare = mongo.db.users.find_one({"email": request.form["email"]})
    if user_to_compare:
        if bcrypt.hashpw(request.form["password"].encode("utf-8"), user_to_compare["password"]) == user_to_compare["password"]:
            session["username"] = user_to_compare["username"]
            flash('You have been logged in!', 'success')
            return True

    flash('Login unsuccessful. Invalid username/password combinationB.', 'danger')
    return False
    
# Start game ------------------------------------
    
def start_game():
    mongo.db.game_properties.update_one({}, {"$set": {"game_started": True}})
    flash('Game Started!', 'success')
    return get_game_state()
    
    
# CREATE ORDER ====================================================================================
    
# Filter pieces by user -------------------------
    
def filter_pieces_by_user(username):
    user = mongo.db.users.find_one({"username": username})
    pieces = mongo.db.pieces.find()
    return [piece for piece in pieces if piece["owner"] == user["nation"]]
    
# Create order ----------------------------------
    
def create_order(request, pieces, game_state, username):
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
    
        
# ANNOUNCEMENTS ===================================================================================

# Write to file ---------------------------------

def write_to_file(filename, data):
    with open(filename, "a") as file:
        file.writelines(data)

# add announcements -----------------------------

def add_announcements(username, announcement):
    announcement = "({}) {}: {}\n".format(datetime.now().strftime("%H:%M:%S"), username, announcement)
    write_to_file("data/announcements.txt", announcement)

# get announcements -----------------------------
    
def get_announcements():
    announcements_list = []
    with open("data/announcements.txt", "r") as announcements: 
        announcements_list = announcements.readlines()
    return announcements_list


# PROCESS ORDERS ==================================================================================
    
# increment year ------------------------------

def increment_year():
    new_year = (mongo.db.game_properties.find_one()["year"] + 1)
    mongo.db.game_properties.update({}, {"$set": {"year": new_year}})
    
# increment phase ------------------------------

def increment_phase():
    new_phase = ((mongo.db.game_properties.find_one()["phase"] + 1) % 7)
    mongo.db.game_properties.update({}, {"$set": {"phase": new_phase}})
    if new_phase == 0: 
        increment_year()
        
# target has shared coast with origin
def territory_shares_coast_with_origin(origin, territory):
    for neighbour in territories[territory]["neighbours"]:
            if neighbour["name"] == origin:
                return neighbour["shared_coast"]
     
# target is accessible by piece_type -------------
def territory_is_accessible_by_piece_type(origin, territory, piece):
    territory_type = territories[territory]["territory_type"]
    if piece["piece_type"] == "a":
        return territory_type != "water"
    else:
        return territory_type == "water" or (territory_type == "coastal" and territory_shares_coast_with_origin(origin, territory))
        
# territory is neighbour ----------------------------

def territory_is_neighbour(origin, territory):
    neighbours = territories[origin]["neighbours"]
    return any(neighbour["name"] == territory for neighbour in neighbours)
        
# piece exists and_belongs to user --------------

def piece_exists_and_belongs_to_user(order, pieces):
    for piece in pieces:
        if order["origin"] == piece["territory"] and order["nation"] == piece["owner"]:
            return piece
    print("invalid move. there is no piece at this origin or it does not belong to the user.")
    return False
    
    
# SURELY THIS CAN BE REFACTORED??
# check for neighbour convoy --------------------

def check_for_neighbour_convoy(order, piece, origin):
    print("checking if neighbour of {0} is convoying {1}".format(origin, order["origin"]))
    """ find out if a piece has any neighbours that are convoying it """
    # get neighbours of territory
    neighbours = territories[origin]["neighbours"]
    print("NEIGHBOURS: {}".format(neighbours))
    print("PIECE CONVOYED BY: {}".format(piece["convoyed_by"]))
    for neighbour in neighbours:
        # if any neighbour is in the convoy dict
        if neighbour["name"] in piece["convoyed_by"] and neighbour["name"] != origin:
            print("YES")
            # check if that neighbour is a neihgbour of the target
            if territory_is_neighbour(neighbour["name"], order["target"]):
                print("one of the neighbours of {0}, {1}, is convoying {2} and is a neighbour of the target.".format(piece["territory"], neighbour["name"], order["origin"]))
                return True
            # if it isn't, check if that neighbour has a neighbour which is convoying the piece
            else: 
                print("{0} has a convoying neighbour, {1}, but {1} is not neighbouring the target. checking if {1} has a neighbour which is convoying {2}".format(piece["territory"], neighbour["name"], order["origin"]))
                # if it doesn't it will be false
                check_for_neighbour_convoy(order, piece, neighbour["name"])
    print("{0} has no neighbour that is convoying {1}".format(piece["territory"], order["origin"]))
    return False

    
# target accessible by convoy -------------------

def target_accessible_by_convoy(order, piece):
    return check_for_neighbour_convoy(order, piece, order["origin"])
    
# move is valid ---------------------------------

def move_is_valid(order, pieces):
    piece = piece_exists_and_belongs_to_user(order, pieces)
    if not piece:
        print("invalid move. there is no piece at this origin or it does not belong to the user.")
        return False
    return (target_accessible_by_convoy(order, piece) or territory_is_neighbour(order["origin"], order["target"])) and territory_is_accessible_by_piece_type(order["origin"], order["target"], piece)
        
# process move ----------------------------------

def process_move(order, pieces):
    if not move_is_valid(order, pieces):
        return False
    mongo.db.pieces.update_one({"territory": order["origin"]}, {"$set": {"challenging": order["target"]}})
    return True
    
# supported piece exists ------------------------

def supported_piece_exists(order, pieces):
    for piece in pieces:
        if order["object"] == piece["territory"]:
            return piece
    print("invalid move. there is no piece in this territory to support.")
    return False
    
# support is valid --------------------------------
# REFACTOR? - could use same as move
def support_is_valid(order, pieces):
    piece = piece_exists_and_belongs_to_user(order, pieces)
    if not piece:
        print("invalid move. there is no piece at this origin or it does not belong to the user.")
        return False
    if not territory_is_neighbour(order["origin"], order["target"]):
        print("invalid move. target is not neighbour.")
        return False
    if not territory_is_accessible_by_piece_type(order["origin"], order["target"], piece):
        print("invalid move. target is not accessible.")
        return False
    if not supported_piece_exists(order, pieces):
        return False
    return True
    
# process support ----------------------------------

def process_support(order, pieces):
    if not support_is_valid(order, pieces):
        return False
    # check if support already exists
    object_supports = mongo.db.pieces.find_one({"territory": order["object"]})["support"]
    if order["target"] in object_supports:
        object_supports[order["target"]] +=1
    else:
        object_supports.update({order["target"]: 1})
    mongo.db.pieces.update({"territory": order["object"]}, {"$set":{"support": object_supports}})
    return True
    
# supported piece exists ------------------------

def convoyed_piece_exists(order, pieces):
    for piece in pieces:
        if order["object"] == piece["territory"]:
            return True
    print("invalid move. there is no piece in this territory to support.")
    return False
    
# piece is on water ------------------------------

def piece_is_on_water(order):
    if territories[order["origin"]]["territory_type"] == "water":
        return True
    print("{}: invalid move. piece must be on water to convoy.".format(order["origin"]))
    return False
    
# convoy is valid --------------------------------

def convoy_is_valid(order, pieces):
    return piece_exists_and_belongs_to_user(order, pieces) and convoyed_piece_exists(order, pieces) and piece_is_on_water(order)
    
# process convoy --------------------------------

def process_convoy(order, pieces):
    if not convoy_is_valid(order, pieces):
        return False
    print("CONVOY SUCCESSFUL: ".format)
    mongo.db.pieces.update({"territory": order["object"]}, {"$push": {"convoyed_by": order["origin"]}})
    return True
        
# process orders ------------------------------

# REFACTOR?
def process_orders(orders, pieces):
    # convoy before move
    for order in orders:
        if order["command"] == "convoy":
            order["order_is_valid"] = process_convoy(order, get_pieces())
    for order in orders:
        if order["command"] == "move":
            order["order_is_valid"] = process_move(order, get_pieces())
    for order in orders:
        if order["command"] == "support":
            order["order_is_valid"] = process_support(order, get_pieces())
    return pieces

# unfinalise_users ----------------------------

def unfinalise_users():
    mongo.db.users.update({}, {"$set": {"orders_finalised": False}}, multi=True)

# get orders ---------------------------------

def get_orders():
    return [order for order in mongo.db.orders.find()]

# get pieces ---------------------------------

def get_pieces():
    return [piece for piece in mongo.db.pieces.find()]

# end_turn -----------------------------

def end_turn():
    unfinalise_users()
    pieces = get_pieces()
    orders = get_orders()
    pieces = process_orders(orders, pieces)
    
    increment_phase()
    # save_orders_to_log()
    # clear orders

    flash('Orders proccessed!', 'success')


# GET GAME STATE ===================================================================================

def get_game_state():
    
    game_state = {
        "pieces" : [record for record in mongo.db.pieces.find()],
        "ownership": mongo.db.ownership.find_one(),
        "orders": [record for record in mongo.db.orders.find()],
        "game_properties": mongo.db.game_properties.find_one(),
    }
    return(game_state)

import random
from orders import initial_orders
from run import mongo
from flask import abort, Response, flash
from territories import territories