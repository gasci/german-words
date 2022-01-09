import os

code = "FLASK_APP=app.py FLASK_ENV=development flask run --port 8080 --host 0.0.0.0"

os.system(code)
