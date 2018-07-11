import os
from flask import Flask, redirect, render_template, request, flash
from flask_pymongo import PyMongo
from game_engine import available_nations, initialise_game_state, create_player, get_game_state

app = Flask(__name__)
app.secret_key = "some_secret"
app.config["MONGO_URI"] = "mongodb://diplomacy-johnpooch.c9users.io/myDatabase"
mongo = PyMongo(app)

# Stores messages between requests
game_state = {}

@app.route("/")
def board():
    game_state = get_game_state()
    return render_template("board.html", game_state = game_state)
    
@app.route("/login")
def login():
    return render_template("login.html")
    
@app.route("/orders", methods=["GET", "POST"])
def orders():
    if request.method == "POST":
        flash("Thanks {}, your orders have been finalised.".format(request.form["name"]))
    return render_template("orders.html")
    
@app.route("/messages")
def messages():
    return render_template("messages.html")
    
@app.route("/announcements")
def announcements():
    return render_template("announcements.html")

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8080)), 
            debug=True)