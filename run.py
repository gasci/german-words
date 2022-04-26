import os
from dotenv import load_dotenv

load_dotenv()

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE")

code = f"FLASK_APP=app.py FLASK_ENV={DEVELOPMENT_MODE} flask run --port 8080"

os.system(code)
