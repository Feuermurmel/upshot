#! /usr/bin/env bash

set -e -o pipefail

cd "$(dirname "$BASH_SOURCE")"

VENV_PATH='venv'

rm -rf "$VENV_PATH"
virtualenv -p python3 "$VENV_PATH"
. "$VENV_PATH/bin/activate"

python setup.py develop
pip install pytest

pip install nodeenv
nodeenv -p --prebuilt
npm install -g katex
