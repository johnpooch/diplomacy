import os
from flask import Flask, redirect, render_template, request
from flask_pymongo import PyMongo
from game_engine import available_nations, initialise_game_state, create_player

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://diplomacy-johnpooch.c9users.io/myDatabase"
mongo = PyMongo(app)

# Stores messages between requests
messages = []
game_state = {}

@app.route("/")
def get_index():
    if available_nations:
        print(avaliable_nations)
        return render_template("index.html")
    else:
        return render_template("board.html", game_state = game_state)
    
    
@app.route("/login")
def do_login():
    username = request.args['username']
    create_player(username)
    return redirect(username)
    

@app.route("/<username>")
def get_userpage(username):
    return render_template("chat.html", logged_in_as=username, all_the_messages=messages)


@app.route("/new", methods=["POST"])
def add_message():
    username = request.form['username']
    text = request.form['message']
    
    words = text.split()
    naughtyWords = set(["dang", "crud", "willy", "fudge"])
    words = [ "*" * len(word) if word.lower() in naughtyWords else word for word in words]
    
    text = " ".join(map(str, words))
    
    message = {
        'sender': username,
        'body': text,
    }
    
    messages.append(message)
    return redirect(username)

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))