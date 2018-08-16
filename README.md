# Diplomacy

Diplomacy is a popular strategy board game released in 1959 by Allan B. Calhamer. The game is set in early 1900s Europe. Diplomacy is known for it's emphasis on negotiation, alliance, and betrayal. Unlike many other strategy board games, Diplomacy does not rely on dice rolling or other random elements. All players write down their orders and at the end of each negotiation phase, all of the orders are processed simultaneously. Typically the game is played by seven players, each controlling one country. Variations of the game allow for fewer players. Variations of the game board also exist. 

This project is designed to be an easy-to-use used browser-based version of Diplomacy which features real-time communication between players and a minimalist user interface which allows players to comfortably study the board while engaging in communications or issuing orders.

This project is built using HTML5, CSS, JavaScript (AJAX and jQuery), Python3, Flask, and Mongo DB (PyMongo). The code is tested using the Python unittest framework. The logic behind the order processing is done using object oriented programming principles. Real time communication between players is achieved using the flask_socketio library.

The project is in a unfinished state. The project is not ready for real-world play-testing and some core functionality is incomplete. 

Live version of the game: http://johnpooch-diplomacy.herokuapp.com/initialise

Note -- to automatically sign in and populate the game with opponents, enter the following link after initialising the game:
http://johnpooch-diplomacy.herokuapp.com/populate

Game Rules: https://www.wizards.com/avalonhill/rules/diplomacy.pdf

## Getting Started

Follow these instructions to run the game locally. 

### Installation

Clone this workspace and install the required software:

```
pip3 install -r requirements.txt
```

or if you're using Cloud9:

```
sudo pip3 install -r requirements.txt
```

The code relies on a Mongo database. To create a Mongo database consult the mLab documentation: https://docs.mlab.com/

Once you have created a Mongo database, create an environment variable for the Mongo URI. You will also need to create a secret key. You can generate a random secret key here: https://randomkeygen.com/

```
$ export MONGO_URI=<INSERT MONGO URI HERE>
$ export SECRET_KEY="<INSERT KEY HERE>"
```

You should now be able to run the game locally:

```
$ python3 run.py
```

### Running the tests

At present, the project only features automated tests which test the logic behind processing orders. To carry out the automated tests, run the following:

```
$ python3 test_order.py
```

## General Comments / What I've Learned From This Project So Far

xxx

## Current Issues

The project has a large number of issues which need to be resolved before the project is ready for play-testing.

## Future Development Plans

xxx

## Built With

* [Flask](http://flask.pocoo.org/) - The flask web framework
* [PyMongo](https://api.mongodb.com/python/current/) - Used to work with Mongo data base
* [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/) - Used for real-time communication between players


## Acknowledgments

* Corey Schafer's video series on working with Flask: https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH
* Pretty Printed's video series on working with SocketIO in Flask: https://www.youtube.com/watch?v=RdSrkkrj3l4&t=6s