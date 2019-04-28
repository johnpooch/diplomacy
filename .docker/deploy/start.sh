#!/bin/bash

echo Running migrations...
python manage.py migrate

while [ 1 ]
do
    echo Starting Runserver.
    python manage.py runserver 0.0.0.0:8000
    sleep 5
done
