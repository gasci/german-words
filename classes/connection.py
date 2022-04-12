import os

from dotenv import load_dotenv
from pymongo import MongoClient

class Connection:

    def __init__(self, env_location):
        
        # load variables
        load_dotenv(env_location)
        
        mongo_cli_username = os.getenv("MONGO_CLI_USERNAME")
        mongo_cli_password = os.getenv("MONGO_CLI_PW")
        mongo_cli_database = os.getenv("MONGO_CLI_DATABASE")
        cluster_name = os.getenv("MONGO_CLI_CLUSTER")

        self.client = MongoClient(
            "mongodb+srv://{}:{}@{}.plop5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE".format(
                mongo_cli_username, mongo_cli_password, cluster_name
            )
        )

        self.data = self.client[mongo_cli_database]
