import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, flash, request, url_for, session
from flask_pymongo import PyMongo
import bcrypt
from game_engine import *
from territories import territories

from wtforms.validators import DataRequired
import pymongo
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "^b$#s3uwbysorx2f3uowzzlxucw8j3stqu7!^452*&i-&ab3g%"

# Vars ------------------------------------------

game_state = {}

# Mongo -----------------------------------------

app.config["MONGO_DBNAME"] = "diplomacydb"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

# -----------------------------------------------
    
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
        create_order(request, pieces, game_state, username)
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

# fill_orders -----------------------------------

@app.route("/fill")
def fill():
    fill_out_orders()
    return redirect(url_for('board'))

# process_orders -----------------------------------

@app.route("/process")
def process():
    end_turn()
    return redirect(url_for('board'))

# initialise ------------------------------------

@app.route("/initialise")
def initialise():
    initialise_game_db()
    return redirect(url_for('board'))
    
# test ------------------------------------

@app.route("/test")
def test():
    initialise_game_db()
    populate_users()
    fill_out_orders()
    end_turn()
    return redirect(url_for('board'))

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8080)), 
            debug=True)