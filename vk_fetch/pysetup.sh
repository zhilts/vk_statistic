#!/usr/bin/env bash

VENV_PATH=env

virtualenv --python=python3 $VENV_PATH

source $VENV_PATH/bin/activate

pip3 install -r ./settings/requirements.txt

if [ "$1" == "--dev" ]; then
    pip3 install -r ./settings/requirements-dev.txt
fi

deactivate