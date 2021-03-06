import repackage

repackage.up()
from classes.connection import Connection
from classes.static_vars import StaticVars

from bson.objectid import ObjectId
import datetime

class AutoUpdate(StaticVars):

    def __init__(self, env_location) -> None:

        super().__init__()

        conn = Connection(env_location)

        self.words = conn.data["words"]

    def update_difficulty(self, word_id, diff):

            last_diff_update = datetime.datetime.now()
            self.words.update_many(
                {"_id": ObjectId(word_id)},
                {"$set": {"difficulty": diff, "last_diff_update": last_diff_update}}
            )

    def auto_update_difficulty(self):
        words = self.words.find(
            {"difficulty": {"$lt": 2}}
        )
        now = datetime.datetime.now()

        for word in words:
            try:
                last_diff_update = word["last_diff_update"]
                diff = int(word["difficulty"])

                if diff == 0:
                    day_diff = self.AUTO_DIFF_EASY_TO_MEDIUM_PERIOD

                elif diff == 1:
                    day_diff = self.AUTO_DIFF_MEDIUM_TO_HARD_PERIOD

                if (now - last_diff_update).days > day_diff:
                    diff += 1

                    self.update_difficulty(word["_id"], min(diff, 2))
            except KeyError:
                self.words.update_many(
                    {"_id": ObjectId(word["_id"])},
                    {"$set": {"difficulty": 2, "last_diff_update": now}}
                )

auto_update = AutoUpdate(".env")
auto_update.auto_update_difficulty()