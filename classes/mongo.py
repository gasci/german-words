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

    def add_update_word(self, word_id, word_dict, update=False):

        user_id = session["user_id"]
        
        # don't add the same word twice
        self.delete_word_by_name(word_dict)

        # words are hard by default
        if not update:
            word_dict["difficulty"] = 2

        #phrases have default sentences  
        if word_dict["type"] == "phrase":
            word_dict["sentence"] = "phrase"
        
        self.words.update_one(
            {"_id": ObjectId(word_id), "user_id": ObjectId(user_id)},
            {"$set": word_dict},
            upsert=True,
        )

    def reset_word_difficulties(self):
        user_id = session["user_id"]
        self.words.update(
            {"user_id": ObjectId(user_id)}, {"$set": {"difficulty": 2}}, multi=True
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

    def get_type_word_ids(self, type, diff=3):

        user_id = session["user_id"]
        if type:
            if diff != 3:
                ids = self.words.find(
                    {
                        "user_id": ObjectId(user_id),
                        "type": type,
                        "difficulty": diff,
                        "sentence": {"$ne": ""},
                    }
                ).distinct("_id")
            else:
                ids = self.words.find(
                    {
                        "user_id": ObjectId(user_id),
                        "type": type,
                        
                    }
                ).distinct("_id")
        else:
            if diff != 3:
                ids = self.words.find(
                    {
                        "user_id": ObjectId(user_id),
                        "difficulty": diff,
                        "sentence": {"$ne": ""},
                    }
                ).distinct("_id")
            else:
                ids = self.words.find(
                    {"user_id": ObjectId(user_id)}
                ).distinct("_id")
        return ids

    def update_difficulty(self, word_id, diff):
        user_id = session["user_id"]
        self.words.update(
            {"_id": ObjectId(word_id), "user_id": ObjectId(user_id)},
            {"$set": {"difficulty": diff}},
            multi=True,
        )

    def count_words(self, type=""):
        user_id = session["user_id"]
        type_list = []

        if type:
            type_list.append(type)
        else:
            type_list = self.list_types()

        # print(type)
        # print(type_list)

        cursor = self.words.aggregate(
            [
                {
                    "$facet": {
                        "All": [
                            {
                                "$match": {
                                    "difficulty": {"$exists": True},
                                    "type": {"$in": type_list},
                                    "sentence": {"$ne": ""},
                                    "user_id": ObjectId(user_id),
                                }
                            },
                            {"$count": "All"},
                        ],
                        "Easy": [
                            {
                                "$match": {
                                    "difficulty": 0,
                                    "type": {"$in": type_list},
                                    "sentence": {"$ne": ""},
                                    "user_id": ObjectId(user_id),
                                }
                            },
                            {"$count": "Easy"},
                        ],
                        "Medium": [
                            {
                                "$match": {
                                    "difficulty": 1,
                                    "type": {"$in": type_list},
                                    "sentence": {"$ne": ""},
                                    "user_id": ObjectId(user_id),
                                }
                            },
                            {"$count": "Medium"},
                        ],
                        "Hard": [
                            {
                                "$match": {
                                    "difficulty": 2,
                                    "type": {"$in": type_list},
                                    "sentence": {"$ne": ""},
                                    "user_id": ObjectId(user_id),
                                }
                            },
                            {"$count": "Hard"},
                        ],
                    }
                },
                {
                    "$project": {
                        "All": {"$arrayElemAt": ["$All.All", 0]},
                        "Easy": {"$arrayElemAt": ["$Easy.Easy", 0]},
                        "Medium": {"$arrayElemAt": ["$Medium.Medium", 0]},
                        "Hard": {"$arrayElemAt": ["$Hard.Hard", 0]},
                    }
                },
            ]
        )

        results = []
        for item in cursor:
            results.append(item)

        return results[0]

    def search_word(self, search_term):
        user_id = session["user_id"]
        result_list = []

        cursor = self.words.find(
            {
                "word": {"$regex": f"{search_term}.*", "$options": "i"},
                "user_id": ObjectId(user_id),
            }
        )

        for result in cursor:
            result_list.append(result)

        return result_list

    def get_words_without_sentence(self):
        user_id = session["user_id"]
        result_list = []

        cursor = self.words.find(
            {"user_id": ObjectId(user_id), "type": {"$ne": "phrase"}, "sentence": ""}
        )

        for result in cursor:
            result_list.append(result)

        return result_list
