
import os

from dotenv import load_dotenv
from pymongo import MongoClient

from bson.objectid import ObjectId


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
        self.words = self.data["words"]

         # create index
        self.words.create_index([('word', 'text')])

    def add_update_word(self, word_id, word_dict):
        self.words.update(
            {"_id": ObjectId(word_id)}, {"$set": word_dict}, upsert=True
        )

    def list_types(self):
        types = self.words.distinct("type")
        return types

    def get_words_type(self, type):
        result_list = []   
        cursor = self.words.find({"type": type})

        for result in cursor:
            result_list.append((result["word"], result["_id"]))
        
        return result_list

    def delete_word(self, word_id):
        self.words.delete_one({"_id": ObjectId(word_id)})

    def get_word(self, word_id):
        cursor = self.words.find({"_id": ObjectId(word_id)})
        return cursor[0]

    def search_word(self, word):
        
        result_list = []    
        cursor = self.words.find( { "$text": { "$search": word } }) 
        
        for result in cursor:
            result_list.append(result)

        if len(result_list) > 0:
            return result_list[0]
        else:
            return []

            
            
