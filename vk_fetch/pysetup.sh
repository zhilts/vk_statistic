#!/usr/bin/env bash

VENV_PATH=env

virtualenv --python=python3 $VENV_PATH

./pyenv.sh python -m pip install -U pip
./pyenv.sh pip install -r ./settings/requirements.txt

if [ "$1" == "--dev" ]; then
    ./pyenv.sh pip install -r ./settings/requirements-dev.txt
fi
