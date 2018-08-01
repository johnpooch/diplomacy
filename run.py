from dependencies import *
from process_orders import end_turn
from player import player
from get_game_state import get_game_state

# Create player -----------------------------------------------------------------------------------
    
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

# ROUTES ==========================================================================================

# board -----------------------------------------

@app.route("/")
def board():
    return render_template("board.html", armies = Army.all_armies, fleets = Fleet.all_fleets, game_properties = game_properties, session = session)

# register --------------------------------------
    
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        users = mongo.db.users
        if not users.find_one({"username": request.form["username"]}):
            session["username"] = create_player(request) # returns username
            return redirect(url_for('board'))
        else:
            flash('That username already exists', 'danger')
    return render_template("register.html", form = form, game_state = get_game_state())
    
# login -----------------------------------------
    
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        
        if attempt_login(request):
            return redirect(url_for('board'))
        else:
            flash('Login unsuccessful. Invalid username/password combination.', 'danger')
            
    return render_template("login.html", form = form, game_state = get_game_state())
    
# logout -----------------------------------------
    
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session["username"] = None
    flash('You have been logged out.', 'success')
    return redirect(url_for('board'))
    
# orders ----------------------------------------
    
@app.route("/orders", methods=["GET", "POST"])
def orders():
    if not "username" in session:
        print('yo')
        return redirect(url_for('register'))
    
    game_state = get_game_state()
    username = session["username"]
    
    pieces = filter_pieces_by_user(username)
        
    if request.method == "POST":
        upload_order_to_db(request, pieces, game_state, username)
        return redirect(url_for('board'))
            
    return render_template("orders.html", pieces = pieces, territories = territories, game_state = game_state)

# finalised -------------------------------------
    
@app.route("/finalised",)
def finalised():
    game_state = get_game_state()
    return render_template("finalised.html", game_state = game_state)

# edit orders -----------------------------------
    
@app.route("/edit_orders", methods=["GET", "POST"])
def edit_orders():
    username = session["username"]
    
    if not mongo.db.users.find_one({"username": username })["orders_finalised"]:
        return "you have not submitted your orders"
    game_state = get_game_state()
    pieces = filter_pieces_by_user(username)
        
    if request.method == "POST":
        # edit_order(request, pieces, game_state, username)
        return redirect(url_for('board'))
            
    return render_template("edit_orders.html", pieces = pieces, territories = territories, game_state = game_state)

# announcements ---------------------------------
    
@app.route("/announcements/")
def announcements():
    announcements = get_announcements()
    return render_template("announcements.html", announcements = announcements)
    
# -----------------------------------------------
    
    
# add announcements ----------------------------- 

@app.route("/announcements/<username>/<announcement>")
def post_announcement(username, announcement):
    add_announcements(username, announcement)
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
    populate_users()
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
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8080)), 
            debug=True)