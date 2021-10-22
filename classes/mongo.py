import os

from dotenv import load_dotenv
from pymongo import MongoClient

from bson.objectid import ObjectId
from flask import session


class Database:
    def __init__(self, env_location):

        # load variables
        load_dotenv(env_location)

        mongo_cli_username = os.environ.get("MONGO_CLI_USERNAME")
        mongo_cli_password = os.environ.get("MONGO_CLI_PW")
        mongo_cli_database = os.environ.get("MONGO_CLI_DATABASE")
        cluster_name = os.environ.get("MONGO_CLI_CLUSTER")

        self.client = MongoClient(
            "mongodb+srv://{}:{}@{}.plop5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE".format(
                mongo_cli_username, mongo_cli_password, cluster_name
            )
        )

        self.data = self.client[mongo_cli_database]
        self.users = self.data["users"]
        self.words = self.data["words"]

        # create index
        self.words.create_index([("word", "text")])

    def add_update_word(self, word_id, word_dict):
        user_id = session["user_id"]
        # don't add the same word twice
        self.delete_word_by_name(word_dict)
        word_dict["difficulty"] = 1
        self.words.update_one(
            {"_id": ObjectId(word_id), "user_id": ObjectId(user_id)},
            {"$set": word_dict},
            upsert=True,
        )

    def list_types(self):
        user_id = session["user_id"]
        types = self.words.find({"user_id": ObjectId(user_id)}).distinct("type")
        return types

    def get_current_user(self):
        user_id = session["user_id"]
        cursor = self.users.find({"_id": ObjectId(user_id)})
        return cursor[0]

    def update_password(self, password):
        user_id = session["user_id"]
        self.users.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"password": password}}
        )

    def get_words_type(self, type):
        user_id = session["user_id"]
        cursor = self.words.find({"type": type, "user_id": ObjectId(user_id)})

        result_list = []
        for result in cursor:
            result_list.append(result)

        return result_list

    def delete_word(self, word_id):
        user_id = session["user_id"]
        self.words.delete_one({"_id": ObjectId(word_id), "user_id": ObjectId(user_id)})

    def delete_word_by_name(self, word_dict):
        user_id = session["user_id"]
        self.words.delete_one(
            {
                "word": word_dict["word"],
                "type": word_dict["type"],
                "user_id": ObjectId(user_id),
            }
        )

    def get_word(self, word_id):
        user_id = session["user_id"]
        cursor = self.words.find(
            {"_id": ObjectId(word_id), "user_id": ObjectId(user_id)}
        )
        return cursor[0]

    def get_type_word_ids(self, type, diff=2):

        user_id = session["user_id"]
        if type:
            if diff != 2:
                ids = self.words.find(
                    {"user_id": ObjectId(user_id), "type": type, "difficulty": diff}
                ).distinct("_id")
            else:
                ids = self.words.find(
                    {"user_id": ObjectId(user_id), "type": type}
                ).distinct("_id")
        else:
            if diff != 2:
                ids = self.words.find(
                    {"user_id": ObjectId(user_id), "difficulty": diff}
                ).distinct("_id")
            else:
                ids = self.words.find({"user_id": ObjectId(user_id)}).distinct("_id")
        return ids

    def update_difficulty(self, word_id, diff):
        user_id = session["user_id"]
        word_dict = self.words.find(
            {"_id": ObjectId(word_id), "user_id": ObjectId(user_id)}
        )[0]
        word_dict["difficulty"] = diff
        self.words.update(
            {"_id": ObjectId(word_id), "user_id": ObjectId(user_id)},
            {"$set": word_dict},
            upsert=True,
        )

    def search_word(self, search_term):
        user_id = session["user_id"]
        result_list = []

        cursor = self.words.find(
            {
                "$text": {"$search": search_term},
                "user_id": ObjectId(user_id),
            },
            {"score": {"$meta": "textScore"}},
        )

        for result in cursor:
            result_list.append(result)

        print(search_term)
        print(result_list)

        return result_list
