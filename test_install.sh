#!/bin/bash
set -e
set -x

python3 -m venv /tmp/testenv
source /tmp/testenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Running main.py"
python main.py
echo "Finished python script"
deactivate
rm -rf /tmp/testenv
