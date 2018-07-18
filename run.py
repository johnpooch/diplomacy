from dependencies import *
from end_turn import end_turn
from setup import initialise_game_db, populate_users, fill_out_orders, start_game
from get_game_state import get_game_state
from create_order import filter_pieces_by_user, upload_order_to_db
    
# ROUTES ==========================================================================================

# board -----------------------------------------

@app.route("/")
def board():
    game_state = get_game_state()
    
    # if no players are registered, initialise db
    if not mongo.db.users.count():
        initialise_game_db()
        return redirect(url_for("register"))
        
    # if seven players are registered, start game
    if mongo.db.users.count() >= 7 and not game_state["game_properties"]["game_started"]:
        game_state = start_game()
        
    # if all players have finalised order, process orders
    if all(user["orders_finalised"] for user in mongo.db.users.find()):
        
        # end_turn()
        print("hello")
    
    return render_template("board.html", game_state = game_state, session = session)

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
    game_state = get_game_state()
    username = session["username"]
    if mongo.db.users.find_one({"username": username })["orders_finalised"]:
        return redirect(url_for("finalised"))
    
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
    fill_out_orders("game_histories/game_1/01_spring_1901.txt")
    end_turn()
    return redirect(url_for('board'))
    
    
# test_2 ------------------------------------

@app.route("/test_2")
def test_2():
    fill_out_orders("game_histories/game_1/02_fall_1901.txt")
    end_turn()
    return redirect(url_for('board'))
    
@app.route("/test_all") 
def test_all():
    initialise_game_db()
    populate_users()
    fill_out_orders("game_histories/game_1/01_spring_1901.txt")
    end_turn()
    fill_out_orders("game_histories/game_1/02_fall_1901.txt")
    end_turn()
    return redirect(url_for('board'))

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8080)), 
            debug=True)