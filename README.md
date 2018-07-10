# bethel

## Install requirements
pip install -r requirements.txt

## Setup flask env
export FLASK_APP=bethel.py

### if debuging
export FLASK_DEBUG=True

## Run
flask run

### Custom host and port
flask run --host 0.0.0.0 --port 80
