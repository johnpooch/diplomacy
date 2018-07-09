import os
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

@app.route("/")
def get_index():
    return render_template("index.html")

app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)