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

To load the fixtures run `make reset_db && make load_dev_fixtures` from the root directory
(outside container). This builds builds two games.

### Test Coverage

To generate a test coverage report test coverage, run `coverage run manage.py
test` from within the container. Then run `coverage report` to see the results.
