#!/bin/bash

if (( $RUNTIMEINSTALL )); then
    echo Installing any changed requirements...
    .docker/deploy/install_requirements.sh $ENV
fi

if [ $RUNMIGRATIONS ]; then
    echo Running migrations...
    manage migrate
fi

for target in $WAITFOR; do
    wait-for-it $target --timeout=120
done
