import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, flash, request, url_for
from flask_pymongo import PyMongo
from game_engine import available_nations, create_player, get_game_state
from territories import territories
from wtforms import StringField, SubmitField, SelectField, HiddenField, TextField, FieldList, FormField
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
    
    
# Routes ----------------------------------------

@app.route("/")
def board():
    game_state = get_game_state()
    return render_template("board.html", game_state = game_state)
    
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Account created for {}!'.format(form.username.data), 'success')
        return redirect(url_for('board'))
    return render_template("register.html", form = form)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "john@john.com" and form.password.data == "password":
            flash('You have been logged in!', 'success')
            return redirect(url_for('board'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template("login.html", form = form)
    
@app.route("/announcements/")
def display_announcements():
    announcements = get_all_announcements()
    return render_template("announcements.html", announcements = announcements)
    
@app.route("/announcements/<username>/<announcement>")
def post_announcement(username, announcement):
    add_announcements(username, announcement)
    return redirect("announcements")
    
@app.route("/orders", methods=["GET", "POST"])
def orders():
    
    username = "johnpooch"
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
            }
            if command in ["support", "convoy", "move"]:
                order["target"] = request.form[(piece["territory"] + "-target")]
                if command != "move":
                    order["object"] = request.form[(piece["territory"] + "-object")]
            print(order)

    return render_template("orders.html", pieces = filtered_pieces, territories = territories)
  
@app.route("/announcements")
def announcements():
    return render_template("announcements.html")
    
# -----------------------------------------------

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8080)), 
            debug=True)