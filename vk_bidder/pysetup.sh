#!/usr/bin/env bash

VENV_PATH=env

rm -rf $VENV_PATH
virtualenv --python=python3 $VENV_PATH
source $VENV_PATH/bin/activate

pip install -r ./settings/requirements.txt

deactivate