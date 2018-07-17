
import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, flash, request, url_for, session
from flask_pymongo import PyMongo
import pymongo

from wtforms.validators import DataRequired
from forms import RegistrationForm, LoginForm

from orders import initial_orders
from datetime import datetime
import bcrypt
import random

from territories import territories
from write_to_log import write_to_log, clear_log
from initial_game_state import *

from order_text_processor import get_orders_from_txt

app = Flask(__name__)
app.config['SECRET_KEY'] = "^b$#s3uwbysorx2f3uowzzlxucw8j3stqu7!^452*&i-&ab3g%"

# Mongo -----------------------------------------

app.config["MONGO_DBNAME"] = "diplomacydb"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

# -----------------------------------------------