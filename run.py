import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, flash, request, url_for, session
from flask_pymongo import PyMongo
import bcrypt
from game_engine import create_player, get_game_state
from territories import territories
from wtforms import StringField, SubmitField, SelectField, HiddenField, TextField, FieldList, FormField
from initial_game_state import *
from wtforms.validators import DataRequired
import pymongo
from forms import RegistrationForm, LoginForm
from players import players

app = Flask(__name__)
app.config['SECRET_KEY'] = "^b$#s3uwbysorx2f3uowzzlxucw8j3stqu7!^452*&i-&ab3g%"

# Vars ------------------------------------------

game_state = {}

# -----------------------------------------------


# Mongo -----------------------------------------

app.config["MONGO_DBNAME"] = "diplomacydb"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

# -----------------------------------------------


# Functions -------------------------------------
    
def initialise_game():
    mongo.db.pieces.remove({})
    mongo.db.users.remove({})
    mongo.db.ownership.remove({})
    mongo.db.orders.remove({})
    mongo.db.nations.remove({})
    pieces = mongo.db.pieces
    for piece in initial_pieces:
        pieces.insert(piece)
        
    nations = mongo.db.nations
    for nation in initial_nations:
        nations.insert(nation)
    mongo.db.ownership.insert(initial_ownership)


def are_seven_players_registered():
    return mongo.db.users.count() >= 7

def write_to_file(filename, data):
    with open(filename, "a") as file:
        file.writelines(data)

def add_announcements(username, announcement):
    announcement = "({}) {}: {}\n".format(datetime.now().strftime("%H:%M:%S"), username, announcement)
    write_to_file("data/announcements.txt", announcement)
    
def get_all_announcements():
    announcements_list = []
    with open("data/announcements.txt", "r") as announcements: 
        announcements_list = announcements.readlines()
    return announcements_list
    
def get_pieces():
    return mongo.db.pieces.find()

# -----------------------------------------------
    
    
    
# ROUTES ==========================================================================================

# board -----------------------------------------

@app.route("/")
def board():
    if not mongo.db.users.count():
        initialise_game()
        flash('Game initialised!', 'success')
        return redirect(url_for("register"))
    
    game_state = get_game_state()
    return render_template("board.html", game_state = game_state, session = session)
    
# -----------------------------------------------


# register --------------------------------------
    
@app.route("/register", methods=["GET", "POST"])
def register():
    game_state = get_game_state()
    form = RegistrationForm()
    if form.validate_on_submit():
        
        users = mongo.db.users
        # only finds duplicate usernames. should find duiplicate emails too
        existing_user = users.find_one({"username": request.form["username"]})
        
        # refactor?
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form["password"].encode('utf-8'), bcrypt.gensalt())
            nation = create_player(request.form["username"])
            users.insert({"username": request.form["username"], "email": request.form["email"], "password": hashpass, "nation": nation })
            session["username"] = request.form["username"]
            if are_seven_players_registered():
                game_state = get_game_state()
                game_state["game_stated"] = True
            flash('Account created for {}!'.format(form.username.data), 'success')
            return redirect(url_for('board'))
        flash('That username already exists', 'danger')
        
    return render_template("register.html", form = form, game_state = game_state)
    
# -----------------------------------------------
    
    
# login -----------------------------------------
    
@app.route("/login", methods=["GET", "POST"])
def login():
    game_state = get_game_state()
    form = LoginForm()
    if form.validate_on_submit():
        
        users = mongo.db.users
        login_user = users.find_one({"email": request.form["email"]})
        
        # are my log in credentials secure?
        if login_user:
            if bcrypt.hashpw(request.form["password"].encode("utf-8"), login_user["password"]) == login_user["password"]:
                session["username"] = login_user["username"]
                flash('You have been logged in!', 'success')
                return redirect(url_for('board'))
            else:
                flash('Login unsuccessful. Invalid username/password combinationA.', 'danger')
        else:
            flash('Login unsuccessful. Invalid username/password combinationB.', 'danger')
    return render_template("login.html", form = form, game_state = game_state)
    
# -----------------------------------------------


# logout -----------------------------------------
    
@app.route("/logout", methods=["GET", "POST"])
def logout():
    game_state = get_game_state()
    session["username"] = None
    flash('You have been logged out.', 'success')
    return redirect(url_for('board'))
    
# -----------------------------------------------


# orders ----------------------------------------
    
@app.route("/orders", methods=["GET", "POST"])
def orders():
    game_state = get_game_state()
    username = session["username"]
    user_nation = players[username]["nation"]
    filtered_pieces = []
    
    cursor = mongo.db.pieces.find()
    for document in cursor:
        pieces = document["pieces"]
        for piece in pieces: 
            if piece["owner"] == user_nation:
                filtered_pieces.append(piece)
        
    if request.method == "POST":
        for piece in filtered_pieces:
            origin = request.form[(piece["territory"] + "-origin")]
            command = request.form[(piece["territory"] + "-command")]
            order = {
                "origin": origin,
                "command": command,
                # NEED TO GET YEAR AND PHASE 
            }
            if command in ["support", "convoy", "move"]:
                order["target"] = request.form[(piece["territory"] + "-target")]
                if command != "move":
                    order["object"] = request.form[(piece["territory"] + "-object")]
            print(order)
            
    return render_template("orders.html", pieces = filtered_pieces, territories = territories, game_state = game_state)
    
# -----------------------------------------------


# announcements ---------------------------------
    
@app.route("/announcements/")
def announcements():
    announcements = get_all_announcements()
    return render_template("announcements.html", announcements = announcements)
    
# -----------------------------------------------
    
    
# add announcements ----------------------------- 

@app.route("/announcements/<username>/<announcement>")
def post_announcement(username, announcement):
    add_announcements(username, announcement)
    return redirect("announcements")
    
# -----------------------------------------------




if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8080)), 
            debug=True)