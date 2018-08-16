# Diplomacy

Diplomacy is a popular strategy board game released in 1959 by Allan B. Calhamer. The game is set in early 1900s Europe. Diplomacy is known for it's emphasis on negotiation, alliance, and betrayal. Unlike many other strategy board games, Diplomacy does not rely on dice rolling or other random elements. All players write down their orders and at the end of each negotiation phase, all of the orders are processed simultaneously. Typically the game is played by seven players, each controlling one country. Variations of the game allow for fewer players. Variations of the game board also exist. 

This project is designed to be an easy-to-use used browser-based version of Diplomacy which features real-time communication between players and a minimalist user interface which allows players to comfortably study the board while engaging in communications or issuing orders.

This project is built using HTML5, CSS, JavaScript (AJAX and jQuery), Python3, Flask, and Mongo DB (PyMongo). The code is tested using the Python unittest framework. The logic behind the order processing is done using object oriented programming principles. Real time communication between players is achieved using the flask_socketio library.

The project is in a unfinished state. The project is not ready for real-world play-testing and some core functionality is incomplete. 

Live version of the game: http://johnpooch-diplomacy.herokuapp.com/

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

Once you have created a Mongo database, create an environment variable for the Mongo URI. You will also need to create a secret key. You can generate a rondom secret key here: https://randomkeygen.com/

```
$ export MONGO_URI=<INSERT MONGO URI HERE>
$ export SECRET_KEY="<INSERT KEY HERE>"
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc