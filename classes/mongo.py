import json
import os
import re
from dotenv import load_dotenv
from pymongo import MongoClient


class Database:
    def __init__(self, env_location):

        # load variables
        load_dotenv(env_location)

        mongo_cli_username = os.environ.get("MONGO_CLI_USERNAME")
        mongo_cli_password = os.environ.get("MONGO_CLI_PW")
        cluster_name = os.environ.get("MONGO_CLI_CLUSTER")

        self.client = MongoClient(
            "mongodb+srv://{}:{}@{}.plop5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE".format(
                mongo_cli_username, mongo_cli_password, cluster_name
            )
        )

        self.data = self.client[mongo_cli_username]

    def add_update_word(self, type, word_dict):
        self.data[f"{type}s"].update(
            {"word": word_dict["word"]}, {"$set": word_dict}, upsert=True
        )

    def list_colls(self):
        colls = self.data.collection_names()

        return colls

    def get_word(self, type, word):
        results = self.data[type].find({"word": word})
        return results[0]

    def delete_word(self, type, word):
        self.data[type].delete_one({"word": word})

    def search_word(self, word):
        colls = self.list_colls()

        result_list = []    
        for coll in colls:

            self.data[coll].create_index([('word', 'text')])
            cursor = self.data[coll].find( { "$text": { "$search": word } }) 

            
            for result in cursor:
                result_list.append(result)

            print(result_list)

            if len(result_list) > 0:
                return result_list[0]
        return []
            
