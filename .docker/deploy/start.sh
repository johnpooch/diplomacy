#!/bin/bash

echo Waiting for DBs...
.docker/deploy/wait-for-it.sh diplomacy.mysql:3306 --timeout=60 -- echo\
    "Diplomacy DB is up."

echo Running migrations...
python manage.py migrate

while [ 1 ]
do
    echo Starting Runserver.
    python manage.py runserver 0.0.0.0:8000
    sleep 5
done
