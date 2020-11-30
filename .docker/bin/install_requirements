#!/bin/bash

set -e

pip install --user -r requirements.txt --index-url https://pypi.gamer-network.net/gamernetwork/dev/+simple/

ENV=$1

if [ "$ENV" == "dev" ]
then
    pip install --user -r dev_requirements.txt
    pip install --user -r lib_requirements.txt || true
fi

if [ "$ENV" == "test" ] || [ "$ENV" == "dev" ]
then
    echo "skip"
    pip install --user -r test_requirements.txt --index-url https://pypi.gamer-network.net/gamernetwork/dev/+simple/
fi
