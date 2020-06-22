# Diplomacy

A web browser version of the classic strategy board game Diplomacy.

We are massive fans of the game and have been happily using some of the
existing web versions like [Play Diplomacy][play diplomacy],
[Backstabbr][backstabbr], and others for years. We decided to build a new
version of the game to try to bring together and improve on some of the
features of the existing versions. We also wanted to make the project open
source so that it could be maintained by an enthusiastic community of diplomacy
fans.

## Overview

This project consists of the following main components:

* `core` - This is the [Django][django] app that powers the project's back end.
  This is where the models are defined. All functionality relating to the
  database lives here.

* `adjudicator` - In diplomacy, at the end of every turn the orders that each
  player has submitted are interpreted and the board is updated. `adjudicator`
  is a python package which interprets an in-game turn and returns the outcome
  of the orders. The outcome is then interpreted by `core` and the state of the
  game is updated accordingly.

* `service` - This is a [Django Rest Framework][DRF] app that provides the API
  through which the `client` application can interact with `core`.

* `client` - This is [React JS][reactjs] app that acts as the front end of the
  project. The client app is contained in a [separate repo][client].


## Getting started

These instructions will get you started with a copy of the project up on your
local machine for development and testing purposes.

### Prerequisites

We use [Docker][docker] and [Docker Compose][docker-compose] in local
development. Follow the docs to get Docker and Docker Compose installed.

### Configuration

Run the following commands from the root directory to create local copies of
configuration files:

* Run `cp project/settings/local.example.py project/settings/local.py
* Run `cp docker-compose.override.yml.example docker-compose.override.yml`

### Bring up local copy

* Run `docker-compose up` to bring up the project (You can run detached by
  adding `-d` flag)
* Once the containers are up you can run commands from inside the docker
  service container by running `docker exec -it diplomacy_diplomacy.service_1`
  and then running whatever command you like.

## Loading fixtures for development

To load the fixtures run `make reset_db && make dev_fixtures && superuser` from the root directory
(outside container). This resets the database, builds the fixtures in
`fixtures/dev` and creates a superuser with the following credentials:
```
Username: admin
Pw: admin
```
You can sign into the client and the service using these credentials.

## Running the tests

From within the service container run `python3 manage.py test`.

### Linting

Run flake8 to check for code style problems. Run `flake8 .` from the project
root. If there are code style problems they will be displayed.

## Test Coverage

To generate a test coverage report test coverage, run `coverage run manage.py
test` from within the container. Then run `coverage report` to see the results.

[play diplomacy]: https://www.playdiplomacy.com/
[backstabbr]: https://www.backstabbr.com/
[django]: https://www.djangoproject.com/
[DRF]: https://www.django-rest-framework.org/
[reactjs]: https://www.reactjs.org/
[client]: https://www.github.com/samjhayes/diplomacy-client/
[docker]: https://docs.docker.com/
[docker-compose]: https://docs.docker.com/compose/
