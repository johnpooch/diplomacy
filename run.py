from dependencies import *
from flask import jsonify
from flask_socketio import SocketIO, send
from end_turn import end_turn
from create_player import create_player
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
    mongo.db.messages.remove({})
    mongo.db.order_history.remove({})

# initialise game db ------------------------------------------------------------------------------

def initialise_game_db():
    clear_db()
    pieces = mongo.db.pieces
    for piece in initial_pieces:
        pieces.insert(piece)
    mongo.db.ownership.insert(initial_ownership)
    mongo.db.game_properties.insert(initial_game_properties)
    flash('Game initialised!', 'success')

    
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
    
# Check if all orders submitted -------------------------------------------------------------------

def checkAllOrdersSubmitted():
    
    total_orders = 0

    for user in mongo.db.users.find({}):
        total_orders += user["num_orders"]

    print(total_orders)
    
    if(mongo.db.orders.count() == 1):
        
        orders = mongo.db.orders.find({})
        pieces = mongo.db.pieces.find({})
        game_properties = mongo.db.game_properties.find_one({})
        
        end_turn(mongo)
        
        return redirect(url_for('board'))
        


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
    
    game_properties = mongo.db.game_properties.find_one({})
    
    pieces = [piece for piece in mongo.db.pieces.find({})]
    user_pieces = []
        
    if 'username' in session:     
        user = mongo.db.users.find_one({"username": session["username"]})
        
    if user:
        user['orders'] = mongo.db.orders.find({"nation": user["nation"]})
        user_pieces = [piece for piece in mongo.db.pieces.find({"nation": user["nation"]})]
    
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
            
            if order_words[0] == "build":
                order = {
                    "nation" : user["nation"],
                    "command" : order_words[0],
                    "piece_type" : order_words[1],
                    "territory" : order_words[2],
                }
            else: 
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
                orders.update_one({"territory": order["territory"]}, {"$set": order})
            else:
                orders.insert(order)
                mongo.db.users.update_one({"username": session["username"]}, { "$inc": { "orders_submitted": 1 }})
               
    checkAllOrdersSubmitted()
    
    # DOWNLOAD ORDERS
    orders = orders.find({"nation" : user["nation"]})
    user = mongo.db.users.find_one({"username": session["username"]})
    return_orders = []
    return_orders.append({"orders_submitted": user["orders_submitted"], "num_orders": user["num_orders"]})
    
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
def handle_json(json):
    print('received json: ' + str(json))
    
    message_dict = {
        'sender_name': json["sender_name"],
        'sender_nation': json["sender_nation"],
        'text': json["text"]
    }
    mongo.db.messages.insert(message_dict)
    
    send(json, broadcast=True)

# register --------------------------------------
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        session["username"] = create_player(mongo, request) # returns username
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

if __name__ == '__main__':
    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug=True)

     