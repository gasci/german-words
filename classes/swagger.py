from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
import os

class APIDoc:
    def __init__(self, swag):

        # load variables
        load_dotenv()

        self.swag = swag
        self.swag["info"]["version"] = "1.0"
        self.swag["info"]["title"] = "German Words API"

    def get_swag(self):
        return self.swag


class APIDocUI:
    def __init__(self):

        # load variables
        load_dotenv()

        DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE")

        if DEVELOPMENT_MODE == "production":
            self.API_URL_BASE = "https://de-words.herokuapp.com"
        else:
            self.API_URL_BASE = "http://127.0.0.1:8080"

        self.SWAGGER_URL = (
            "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
        )
        self.API_URL = f"{self.API_URL_BASE}/spec"  # Our API url (can of course be a local resource)

    def get_blueprint(self):

        # Call factory function to create our blueprint
        swaggerui_blueprint = get_swaggerui_blueprint(
            self.SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
            self.API_URL,
            config={"app_name": "German words"},  # Swagger UI config overrides
        )

        return swaggerui_blueprint
