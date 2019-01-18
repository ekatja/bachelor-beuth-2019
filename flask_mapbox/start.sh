source activate bachelor3.6
export FLASK_APP=app.py
export FLASK_DEBUG=1
export APP_CONFIG_FILE=settings.py
flask run
deactivate