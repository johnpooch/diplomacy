# Diplomacy

### Introduction to Diplomacy
Diplomacy is a popular strategy board game released in 1959 by Allan B. Calhamer. The game is set in early 1900s Europe. Diplomacy is known for it's emphasis on negotiation, alliance, and betrayal. Unlike many other strategy board games, Diplomacy does not rely on dice rolling or other random elements. All players write down their orders and at the end of each negotiation phase, all of the orders are processed simultaneously. Typically the game is played by seven players, each controlling one country. Variations of the game allow for fewer players. Variations of the game board also exist. 

### Motivations Behind the Project
This project is designed to be an easy-to-use used browser-based version of Diplomacy which features real-time communication between players and a minimalist user interface which allows players to comfortably study the board while engaging in communications or issuing orders.

### Project Stack Overview
This project is built using HTML5, CSS, JavaScript (AJAX and jQuery), Python3, Flask, and Mongo DB (PyMongo). The code is tested using the Python unittest framework. The logic behind the order processing is done using object oriented programming principles. Real time communication between players is achieved using the flask_socketio library.

### Live Version
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
$ pip3 install -r requirements.txt
```

or if you're using Cloud9:

```
$ sudo pip3 install -r requirements.txt
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

* Orders are processed using object oriented programming. This process was originally written in a procedural coding style but it quickly became unsustainable. The advantages of OOP became very clear form this process.

* The interfacing between MongoDB and the OOP sections of the code represented an interesting challenge. Data had to be pulled from the MongoDB, converted into instances of objects, processed, and then converted back to dictionaries and saved.

* Orders represented an interesting opportunity to use inheritence. Order types ('hold', 'move', 'support', 'convoy', 'retreat', 'build') have some shared characteristics but each order has unique attributes and methods. The same is true of the two piece types, 'army' and 'fleet' which both inheit form the Piece class.

* I think I should have used a test driven development approach with this project. As the code became increasingly complex it became more and more difficult to be sure that everything was working as expected. 

* I should have been more clear about what data structures would be used from beginning. By diving head first into the code and not thinking enough about the data structures, I ended up wasting a lot of time and effort.

* I believe there is great value in coding boardgames. Boardgames provide a defined set of often complicated rules and manny interpretations of how to represent data bpard game are possible.

* Keeping functions short and focused on single purposes meant that code maintained its legibility even when the scripts became very long. 


## Current Issues

The project has a large number of issues which need to be resolved before the project is ready for play-testing.

##### Badly written code
There are a number of areas in the source code which are repetitive or unnecessarily complex. Comments have been inserted to identify problematic areas. These will be addressed over time.

##### Confused hierarchy
The hierarchy of User, Piece, and Order classes is confused and this manifests in the form of unnecessarily complex code. 

##### Feedback Bug
There is a bug in the feedback.js code. The code catches most invalid strings. However, if the user ignores an invalid order warning and completes the order, the order will appear as valid. This issue could be fixed by refactoring the code. 
This script could use AJAX. This would mean that the logic of identifying invalid and valid moves could be handled on the backend. I think this would make for more elegant code. 

##### Game End
There is no system in place to end the game. Diplomacy can be won by an individual or as part of a draw. This should be represented in the code.

##### Missing rules
Some rules of the game are not represented in the code. For example, the rule whereby a player can only build a piece in a home territory is not represented.

##### Special Coast
More concise code could be written to handle the special coast edge case with supports.

##### List of abbreviations and rules
Players should have access to a list of valid abbreviations for territories. The rules of the game should also be available.

##### Console errors
Two elements have the same ID which throws an error in the console. The socketIO messagin system also throws errors.



## Future Development Plans

xxx

## Built With

* [Flask](http://flask.pocoo.org/) - The flask web framework
* [PyMongo](https://api.mongodb.com/python/current/) - Used to work with Mongo data base
* [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/) - Used for real-time communication between players


## Acknowledgments

* Corey Schafer's video series on working with Flask: https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH
* Pretty Printed's video series on working with SocketIO in Flask: https://www.youtube.com/watch?v=RdSrkkrj3l4&t=6s