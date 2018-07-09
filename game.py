import os
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

game_state = {
    "pieces": [
        {
            "territory": "par",
            "owner": "france",
            "piece_type": "a",
        },
        {
            "territory": "bur",
            "owner": "germany",
            "piece_type": "f",
        }
    ]
}

@app.route("/")
def get_index():
    return render_template("index.html", game_state = game_state)

app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)