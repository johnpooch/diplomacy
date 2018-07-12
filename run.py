import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, flash
from flask_pymongo import PyMongo
from game_engine import available_nations, initialise_game_state, create_player, get_game_state

app = Flask(__name__)
app.secret_key = "some_secret"
app.config["MONGO_URI"] = "mongodb://diplomacy-johnpooch.c9users.io/myDatabase"
mongo = PyMongo(app)

game_state = {}

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
    if request.method == "POST":
        flash("Thanks {}, your orders have been finalised.".format(request.form["name"]))
    return render_template("orders.html")
    
@app.route("/announcements")
def announcements():
    return render_template("announcements.html")
    
# -----------------------------------------------

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8080)), 
            debug=True)
            
            