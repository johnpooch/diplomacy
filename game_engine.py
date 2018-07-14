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
    return redirect(url_for("register"))
    
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
    
# -----------------------------------------------


# PROCESS ORDERS ==================================================================================

# get orders ---------------------------------

def get_orders():
    return [order for order in mongo.db.orders.find()]

# get pieces ---------------------------------

def get_pieces():
    return [piece for piece in mongo.db.pieces.find()]

# process orders -----------------------------

def process_orders():
    pieces = get_pieces()
    orders = get_orders()

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
from game_state import game_state
from orders import initial_orders
from run import mongo
from flask import abort, Response, flash