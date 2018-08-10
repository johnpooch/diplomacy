from dependencies import *
from flask import jsonify
from flask_socketio import SocketIO, send
from process_orders import *
from nation import Nation
from initial_game_state import initial_pieces, initial_game_properties, initial_ownership, dummy_players
from get_game_state import get_game_state
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Mongo -----------------------------------------

app.config["MONGO_DBNAME"] = "diplomacydb"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

# -----------------------------------------------

# RUN FUNCTIONS ===================================================================================

# fill out orders --------------------------------------------------------------------------------- 

def fill_out_orders(file_name):
    mongo.db.orders.remove({})
    orders = mongo.db.orders
    for order in first_orders:
        orders.insert(order)
        
# Populate Users ----------------------------------------------------------------------------------

""" creates seven dummy users """

def populate_users():
    mongo.db.users.remove({})
    users = mongo.db.users
    for player in dummy_players:
        users.insert(player)
    session["username"] = dummy_players[0]["username"]

# clear db ----------------------------------------------------------------------------------------

def clear_db():
    # NEED TO CLEAR ORDER HISTORY
    mongo.db.pieces.remove({})
    mongo.db.users.remove({})
    mongo.db.ownership.remove({})
    mongo.db.orders.remove({})
    mongo.db.game_properties.remove({})

# initialise game db ------------------------------------------------------------------------------

def initialise_game_db():
    clear_db()
    pieces = mongo.db.pieces
    for piece in initial_pieces:
        pieces.insert(piece)
    mongo.db.ownership.insert(initial_ownership)
    mongo.db.game_properties.insert(initial_game_properties)
    flash('Game initialised!', 'success')

# Create player -----------------------------------------------------------------------------------
    
def create_player(request):
    
    nation = random.choice([nation for nation in mongo.db.nations.find({"available": True})])
    mongo.db.nations.update_one({'_id': nation['_id']}, { '$set': {'available': False}})
    
    player_nation = nation['name']
    if player_nation == "russia":
        num_pieces = 4
    else:
        num_pieces = 3
    
    mongo.db.users.insert(
        {
        "username": request.form["username"],
        "email": request.form["email"],
        "password": request.form["password"],
        "nation": player_nation,
        "orders_submitted": orders_submitted,
        "num_pieces": num_pieces,
        "orders_finalised": False
        }
    )
    flash('Account created for {}!'.format(request.form["username"]), 'success')
    return request.form["username"]
    
# Attempt login -----------------------------------------------------------------------------------

def attempt_login(request):

    user = mongo.db.users.find_one({"email": request.form["email"]})
    if user:
        if request.form["password"] == user["password"]:
            session["username"] = user["username"]
            flash('You have been logged in!', 'success')
            return True

    flash('Login unsuccessful. Invalid username/password combination.', 'danger')
    return False
    
# Update pieces db --------------------------------------------------------------------------------

def update_pieces_db(updated_pieces):
    for piece in updated_pieces:
        print(piece["_id"])
        mongo.db.pieces.update({"_id": piece["_id"]}, 
        {
            "nation": piece["nation"], 
            "piece_type": piece["piece_type"],
            "territory": piece["territory"], 
            "previous_territory": piece["previous_territory"], 
            "retreat": piece["retreat"], 
        })
    return True
    
# Clear db for next turn --------------------------------------------------------------------------

def clear_db_for_next_turn():
    
    for order in mongo.db.orders.find({}):
        mongo.db.order_history.insert(order)
    
    mongo.db.orders.remove({})
    mongo.db.users.update({}, {"$set" : { "orders_submitted" : 0 }})
    
# End turn ----------------------------------------------------------------------------------------

def end_turn(orders, pieces):
    
    orders_to_be_processed = []
    
    for order in orders:
        orders_to_be_processed.append(order)
    
    updated_pieces = process_orders(orders_to_be_processed, pieces)
    print(updated_pieces)
    update_pieces_db(updated_pieces)
    
    clear_db_for_next_turn()
    
    
# Check if all orders submitted -------------------------------------------------------------------

def checkAllOrdersSubmitted():
    
    if(mongo.db.orders.count() == mongo.db.pieces.count()):
        
        orders = mongo.db.orders.find({})
        pieces = mongo.db.pieces.find({})
        
        end_turn(orders, pieces)
        
        return True
    return False


# ROUTES ==========================================================================================

# board -----------------------------------------

@app.route("/")
def board():

    pieces = []
    user = None
    
    # Forms
    registration_form = RegistrationForm()
    login_form = LoginForm()
    
    players = mongo.db.users.find({})
    messages = mongo.db.messages.find({})
    territories = [territory.name for territory in Territory.all_territories]
    
    pieces = [piece for piece in mongo.db.pieces.find({})]
    user_pieces = []
        
    if 'username' in session:     
        user = mongo.db.users.find_one({"username": session["username"]})
        
    if user:
        user['orders'] = mongo.db.orders.find({"nation": user["nation"]})
        user_pieces = [piece for piece in mongo.db.pieces.find({"nation": user["nation"]})]
        
    for piece in pieces:
        print("piece {}".format(piece))
    
    return render_template("board.html", user_pieces = user_pieces, pieces = pieces, game_properties = game_properties, session = session, registration_form = registration_form, login_form = login_form, user = user, players = players, messages = messages, territories = territories)
    
# process ---------------------------------------

@app.route("/process", methods=["POST"])
def process():
    
    orders = mongo.db.orders
    user = mongo.db.users.find_one({"username": session["username"]})
    
    # if delete
    if "id" in request.form:
        orders.delete_one({"_id": ObjectId(request.form["id"])})
        mongo.db.users.update_one({"username": session["username"]}, { "$inc": { "orders_submitted": -1 }})
        
    # if create
    else:
        order_string = request.form["order"]
        
        # UPLOAD ORDER
        if order_string:
            order_words = order_string.split(" ")
            order = {
                "nation" : user["nation"],
                "piece_type" : order_words[0],
                "territory" : order_words[1],
                "command" : order_words[2],
            }
            if order["command"] == 'move':
                order["target"] = order_words[3]
                
            if order["command"] in ['support', 'convoy']:
                order["object"] = order_words[3]
                order["target"] = order_words[4]
                
            if orders.find_one({"territory": order["territory"]}):
                print("order for piece at {} already in db".format( order["territory"]))
                orders.update_one({"territory": order["territory"]}, {"$set": order})
            else:
                print("order for piece at {} not in db".format( order["territory"]))
                orders.insert(order)
                mongo.db.users.update_one({"username": session["username"]}, { "$inc": { "orders_submitted": 1 }})
                
    if checkAllOrdersSubmitted():
        return redirect(url_for('board'))
          
    else:
        # DOWNLOAD ORDERS
        orders = orders.find({"nation" : user["nation"]})
        user = mongo.db.users.find_one({"username": session["username"]})
        return_orders = []
        return_orders.append({"orders_submitted": user["orders_submitted"], "num_pieces": user["num_pieces"]})
        
        for order in orders:
            order_for_js = {
                "id" : str(order["_id"]),
                "piece_type" : order["piece_type"],
                "territory" : order["territory"],
                "command" : order["command"],
            }
            if "target" in order:
                order_for_js["target"] = order["target"]
                
            if "object" in order:
                order_for_js["object"] = order["object"]
        
            return_orders.append(order_for_js)
        
    return jsonify(return_orders)

    
# messages --------------------------------------

@socketio.on('message')
def handle_message(msg):
    
    split_message = msg.split(' - ', 1)
    message_dict = {
        'sender': split_message[0],
        'message': split_message[1]
    }
    
    mongo.db.messages.insert(message_dict)
    send(message_dict["message"], broadcast=True)

# register --------------------------------------
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        session["username"] = create_player(request) # returns username
        return redirect(url_for('board'))
    return redirect(url_for('board'))
    
# login -----------------------------------------
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        attempt_login(request)
    else:
        flash('Form Invalid.', 'danger')
    return redirect(url_for('board'))
    
# logout -----------------------------------------
    
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session["username"] = None
    flash('You have been logged out.', 'success')
    return redirect(url_for('board'))
    
# orders ----------------------------------------
    
@app.route("/orders", methods=["GET", "POST"])
def orders():
    
    if request.method == "POST":
        create_order_dicts(request)
    return redirect(url_for('board'))

# edit orders -----------------------------------
    
@app.route("/edit_orders", methods=["GET", "POST"])
def edit_orders():
        
    if request.method == "POST":
        # edit_order(request, pieces, game_state, username)
        return redirect(url_for('board'))
            
    return redirect(url_for('board'))

# announcements ---------------------------------
    
@app.route("/announcements/")
def announcements():
    announcements = get_announcements()
    return render_template("announcements.html", announcements = announcements)
    
# -----------------------------------------------
    
# clear announcements --------------------------------------

@app.route("/clear_messages")
def clear_messages():
    mongo.db.messages.remove({})
    return redirect(url_for('board'))
    
# add announcement ----------------------------- 

@app.route("/add_announcement")
def post_announcement(username, announcement):
    add_announcement(username, announcement)
    return redirect("announcements")

# populate --------------------------------------

@app.route("/populate")
def populate():
    populate_users()
    return redirect(url_for('board'))

# initialise ------------------------------------

@app.route("/initialise")
def initialise():
    initialise_game_db()
    return redirect(url_for('board'))
    
# test_1 ------------------------------------

@app.route("/test_1")
def test_1():
    end_turn("game_histories/game_1/01_spring_1901.txt")
    return redirect(url_for('board'))
    
    
# test_2 ------------------------------------

@app.route("/test_2")
def test_2():
    end_turn("game_histories/game_1/02_fall_1901.txt")
    return redirect(url_for('board'))
    
@app.route("/test_all") 
def test_all():
    end_turn("game_histories/game_1/01_spring_1901.txt")
    end_turn("game_histories/game_1/02_fall_1901.txt")
    end_turn("game_histories/game_1/03_fall_build_1901.txt")
    
    return redirect(url_for('board'))
    
checkAllOrdersSubmitted()

if __name__ == '__main__':
    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug=True)

     