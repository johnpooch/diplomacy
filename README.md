# Diplomacy

A web browser version of the classic strategy board game 'Diplomacy'.

### Getting started

Copy the example settings file:
`cp project/settings.example.py project/settings.py` and change the
`settings.py` file as necessary for local development:

 * To make the project work without using Docker, uncomment the sections
   labelled `# NOTE non Docker setup` and comment out the corresponding
   sections (which are not commented out by default).

### Loading fixtures for dev

To load the fixtures run `make load_all_fixtures` from the root directory
within service container. This builds the initial state of a game.
