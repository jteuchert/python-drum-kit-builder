#!/bin/bash
set -e

python3 -m venv /tmp/testenv
source /tmp/testenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python kit_builder_v1.py
deactivate
rm -rf /tmp/testenv

