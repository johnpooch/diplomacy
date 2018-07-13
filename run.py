import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, flash, request
from flask_pymongo import PyMongo
from game_engine import available_nations, initialise_game_state, create_player, get_game_state
from territories import territories
from wtforms import StringField, SubmitField, SelectField, HiddenField, TextField, FieldList, FormField
from wtforms.validators import DataRequired
import pymongo
from forms import OrderForm

app = Flask(__name__)
app.secret_key = "some_secret"

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
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        write_to_file("data/users.txt", request.form["username"] + "\n")
        return redirect("")
    return render_template("login.html")
    
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
    form = OrderForm()
    pieces = mongo.db.pieces.find()
    for piece in pieces:
        setattr(form, 'target_2', SelectField('Target', validators=[DataRequired()], choices=[]))
        form.target.choices = [(neighbour, neighbour) for neighbour in territories[piece["territory"]]["neighbours"]]
        form.object.choices = [(neighbour, neighbour) for neighbour in territories[piece["territory"]]["neighbours"]]
    
    if request.method == "POST" and form.validate():
        
        order = {
            "origin": form.origin.name,
            "command": form.command.data,
        }
        if form.command.data in ["support", "convoy", "move"]:
            order["target"] = form.target.data
            if form.command.data != "move":
                order["object"] = form.object.data
        print(order)

    return render_template("orders.html", form = form)
  
@app.route("/announcements")
def announcements():
    return render_template("announcements.html")
    
# -----------------------------------------------

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8080)), 
            debug=True)
            
            