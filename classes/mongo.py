
import datetime

from bson.objectid import ObjectId
from flask import session #, make_response, jsonify
from classes.connection import Connection


class Database:
    def __init__(self, env_location):

        conn = Connection(env_location)

        self.users = conn.data["users"]
        self.words = conn.data["words"]

        # create index
        self.words.create_index([("word", "text")])

        # update a col name
        # self.words.update({}, {'$rename': {'last_update': 'last_diff_update'}}, multi=True)

        self.word_diff_update_refractory_period = 1  # hours
        self.auto_diff_easy_to_medium_period = 10  # days
        self.auto_diff_medium_to_hard_period = 2  # days

    def add_update_word(self, word_id, word_dict, update=False):

        user_id = session["user_id"]
             
        # don't add the same word twice
        self.delete_word_by_name(word_dict)

        # words are hard by default
        if not update:
            word_dict["difficulty"] = 2

        # phrases have default sentences
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

    def count_words_type(self):

        user_id = session["user_id"]

        cursor = self.words.aggregate(
            [
                {"$match": {"user_id": ObjectId(user_id), "type": {"$not": {"$size": 0}}}},
                {"$unwind": "$type"},
                {"$group": {"_id": {"$toLower": "$type"}, "count": {"$sum": 1}}},
                {"$match": {"count": {"$gte": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 100},
                { "$sort" : { "_id" : 1 } }
            ]
        )

        word_type_counts = []
        for item in cursor:
            word_type_counts.append(item)

        return word_type_counts

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

        show_diff_selector = True

        word_dict = cursor[0]

        now = datetime.datetime.now()

        try:
            # can't update a words status for 12 hours
            if word_dict["last_diff_update"] > now - datetime.timedelta(
                hours=self.word_diff_update_refractory_period
            ):
                show_diff_selector = False
        except KeyError:
            pass

        word_dict["show_diff_selector"] = show_diff_selector

        return word_dict

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
                ids = self.words.find({"user_id": ObjectId(user_id)}).distinct("_id")
        return ids

    def update_difficulty(self, word_id, diff):

        last_diff_update = datetime.datetime.now()
        user_id = session["user_id"]
        self.words.update(
            {"_id": ObjectId(word_id), "user_id": ObjectId(user_id)},
            {"$set": {"difficulty": diff, "last_diff_update": last_diff_update}},
            multi=True,
        )

    def auto_update_difficulty(self):
        user_id = session["user_id"]
        words = self.words.find(
            {"user_id": ObjectId(user_id), "difficulty": {"$lt": 2}}
        )
        now = datetime.datetime.now()

        for word in words:
            try:
                last_diff_update = word["last_diff_update"]
                diff = int(word["difficulty"])

                if diff == 0:
                    day_diff = self.auto_diff_easy_to_medium_period

                elif diff == 1:
                    day_diff = self.auto_diff_medium_to_hard_period

                if (now - last_diff_update).days > day_diff:
                    diff += 1
                    self.update_difficulty(word["_id"], min(diff, 2))
            except KeyError:
                self.words.update(
                    {"_id": ObjectId(word["_id"]), "user_id": ObjectId(user_id)},
                    {"$set": {"difficulty": 2, "last_diff_update": now}},
                    multi=True,
                )

    def count_words_diff(self, type=""):
        user_id = session["user_id"]
        type_list = []

        if type:
            type_list.append(type)
        else:
            type_list = self.list_types()

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
