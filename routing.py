import os
from flask import Flask, redirect, render_template, request
from flask_pymongo import PyMongo
from game_engine import available_nations, initialise_game_state, create_player, get_game_state

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://diplomacy-johnpooch.c9users.io/myDatabase"
mongo = PyMongo(app)

# Stores messages between requests
messages = []
game_state = {}

@app.route("/")
def get_index():
    game_state = get_game_state()
    return render_template("board.html", game_state = game_state)
    
@app.route("/login")
def login():
    
    return render_template("login.html")

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))