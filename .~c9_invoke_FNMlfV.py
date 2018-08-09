from dependencies import *
from flask import jsonify
from flask_socketio import SocketIO, send
from process_orders import end_turn
from nation import Nation
from get_game_state import get_game_state

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Mongo -----------------------------------------

app.config["MONGO_DBNAME"] = "diplomacydb"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

# -----------------------------------------------

# ANNOUNCEMENTS ===================================================================================

# Write to file -----------------------------------------------------------------------------------

def write_to_file(filename, data):
    with open(filename, "a") as file:
        file.writelines(data)

# add announcements -------------------------------------------------------------------------------

def add_announcements(username, announcement):
    announcement = "({}) {}: {}\n".format(datetime.now().strftime("%H:%M:%S"), username, announcement)
    write_to_file("data/announcements.txt", announcement)

# get announcements -------------------------------------------------------------------------------
    
def get_announcements():
    announcements_list = []
    with open("data/announcements.txt", "r") as announcements: 
        announcements_list = announcements.readlines()
    return announcements_list
    
# add messages -------------------------------------------------------------------------------

def add_messages(username, message):
    message = "({}) {}: {}\n".format(datetime.now().strftime("%H:%M:%S"), username, message)
    write_to_file("data/messages.txt", message)
    
# get messages -------------------------------------------------------------------------------
    
def get_messages():
    messages_list = []
    with open("data/messages.txt", "r") as announcements: 
        messages_list = messages.readlines()
    return messages_list

# Create order dict -----------------------------------------------------------------------------------

def create_order_dicts(request):
    for key in request.form.keys():
        key_words = key.split()
        value_words = request.form[key].split()
        command = value_words[0]
        order = {
            "nation": key_words[0],
            "territory": key_words[1],
            "command": value_words[0],
        }
        if command in ["move", "retreat"]:
            order["target"] = value_words[1]
            
        if command in ["support", "convoy"]:
            order["object"] = value_words[1]
            order["target"] = value_words[2]
        
        mongo.db.orders.insert(order)
    mongo.db.users.update_one({"username": session["username"]}, { "$set": { "orders_finalised" : True }})

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
        "num_pieces": num_pieces,
        "num_orders": 0,
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
        
    if 'username' in session:     
        user = mongo.db.users.find_one({"username": session["username"]})
        
    if user:
        user['orders'] = mongo.db.orders.find({"nation": user["nation"]})
        pieces = [piece for piece in Piece.all_pieces if piece.nation.name == user["nation"]]
    
    return render_template("board.html", pieces = pieces, armies = Army.all_armies, fleets = Fleet.all_fleets, game_properties = game_properties, session = session, registration_form = registration_form, login_form = login_form, user = user, players = players, messages = messages, territories = territories)
    
# process ---------------------------------------

@app.route("/process", methods=["POST"])
def process():
    order_string = request.form["order"]
    user = mongo.db.users.find_one({"username": session["username"]})
    orders = mongo.db.orders
    
    print(order_string)
    
    # UPLOAD ORDER
    if order_string:
        order_words = order_string.split(" ")
        print("order words: {}".format(order_words))
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
            mongo.db.users.update_one({"username": session["username"]}, { "$inc": { "num_orders": 1,}})
        
    # DOWNLOAD ORDERS
    orders = orders.find({"nation" : user["nation"]})
    user = mongo.db.users.find_one({"username": session["username"]})
    return_orders = []
    return_orders.append({"num_orders": user["num_orders"], "num_pieces": user["num_pieces"]})
    for order in orders:
        
        order_for_js = {
            
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
    
    print(msg)
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
    for nation in mongo.db.nations.find({}):
        mongo.db.nations.update_one(nation, {'$set': {'available': True }})
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

     