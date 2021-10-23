from flask import request, render_template, redirect, session, url_for
from flask_classful import FlaskView, route

from bson.objectid import ObjectId

from classes.mongo import Database
from classes.server import Server
from classes.admin import FlaskAdmin

import json
import bcrypt
import os
from random import shuffle

# import asyncio

server = Server()
app = server.app
db = Database(".env")
admin = FlaskAdmin(app, db)

can_register = os.environ.get("CAN_REGISTER")


@app.route("/", methods=["POST", "GET"])
def starting_url():
    return redirect(url_for("AuthView:login_auth"))


def login_required(func):
    def wrapper(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("AuthView:login_auth"))
        return func(*args, **kwargs)

    return wrapper


class AuthView(FlaskView):

    default_methods = ["GET", "POST"]

    @route("/register", methods=["GET", "POST"])
    def register_auth(self):

        if not can_register == "True":
            message = "Currently, registration is not allowed. Contact: drgoktugasci@gmail.com"
            return render_template("auth/login.html", message=message)

        message = "Please register"
        server.is_authenticated_check()
        if "email" in session:
            return redirect(url_for("MainView:index"))
        if request.method == "POST":

            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            username = request.form.get("username")
            email = request.form.get("email")

            password1 = request.form.get("password1")
            password2 = request.form.get("password2")

            username_found = db.users.find_one({"username": username})
            # email_found = db.users.find_one({"email": email})
            if username_found:
                message = "There already is a user by that username"
                return render_template("auth/register.html", message=message)
            # if email_found:
            #     message = "This email already exists in database"
            #     return render_template("auth/register.html", message=message)
            if password1 != password2:
                message = "Passwords should match!"
                return render_template("auth/register.html", message=message)
            else:
                hashed = bcrypt.hashpw(password2.encode("utf-8"), bcrypt.gensalt())
                user_input = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                    "email": email,
                    "password": hashed,
                }
                db.users.insert_one(user_input)

                user_data = db.users.find_one({"email": email})
                self.create_user_session(user_data)
                server.is_authenticated_check()
                return render_template("index.html")
        return render_template("auth/register.html")

    def create_user_session(self, data):

        for key, value in data.items():
            if key == "_id":
                key = "user_id"
                value = str(value)
            if key not in ["csrf_token", "word_ids", "password"]:
                session[key] = value

    @route("/login", methods=["GET", "POST"])
    def login_auth(self):

        message = ""
        server.is_authenticated_check()
        if "email" in session:
            return redirect(url_for("MainView:index"))

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user_data = db.users.find_one(
                {"$or": [{"email": username}, {"username": username}]}
            )
            if user_data:
                passwordcheck = user_data["password"]

                if bcrypt.checkpw(password.encode("utf-8"), passwordcheck):
                    self.create_user_session(user_data)
                    server.is_authenticated_check()
                    return redirect(url_for("MainView:index"))
                else:
                    message = "Wrong password"
                    return render_template("auth/login.html", message=message)

            else:
                message = "Email not found"
                return render_template("auth/login.html", message=message)
        return render_template("auth/login.html", message=message)

    @route("/logout", methods=["GET", "POST"])
    def logout_auth(self):
        session.clear()
        server.is_authenticated_check()
        return redirect(url_for("AuthView:login_auth"))

    @route("/update_password", methods=["GET", "POST"])
    @login_required
    def update_password_auth(self):
        if request.method == "POST":
            old_password = request.form.get("old_password")
            password = request.form.get("password1")

            user_dict = db.get_current_user()
            password_match = bcrypt.checkpw(
                old_password.encode("utf-8"), user_dict["password"]
            )

            if password_match:
                new_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                db.update_password(new_password)
                return render_template(
                    "profile.html", message="Password updated", user_dict=user_dict
                )

            return render_template(
                "profile.html", message="Old password is wrong", user_dict=user_dict
            )


class MainView(FlaskView):

    default_methods = ["GET", "POST"]

    @login_required
    def index(self):
        types = db.list_types()
        return render_template("index.html", types=types)

    @login_required
    def profile(self):
        user_dict = db.get_current_user()
        return render_template("profile.html", user_dict=user_dict)


class WordView(FlaskView):

    default_methods = ["GET", "POST"]

    @login_required
    def list(self):
        type = request.args.get("type").lower()
        words = db.get_words_type(type)
        return render_template("words.html", words=words, type=type)

    @login_required
    def get_word(self):
        word_id = request.args.get("word_id", False)
        difficulty = request.args.get("difficulty", 2)
        type = request.args.get("type", False)
        shuffle_study = request.args.get("shuffle_study", False)
        shuffle_words = request.args.get("shuffle_words", False)

        if shuffle_study:
            shuffle_study = True

        if shuffle_words:
            shuffle_words = True

        # print(shuffle_study)
        # print(shuffle_words)

        difficulty = int(difficulty)

        if shuffle_words and shuffle_study:
            # print("shuffled")
            ids = [str(x) for x in db.get_type_word_ids(type, difficulty)]
            shuffle(ids)
            # print(ids)
            session["word_ids"] = ids
            if ids:
                word_id = ids[0]
                word_dict = db.get_word(word_id)
        elif not shuffle_words and shuffle_study:
            # print("not shuffled")
            word_dict = db.get_word(word_id)
            ids = session["word_ids"]
            # print(ids)
        else:
            word_dict = db.get_word(word_id)
            ids = [str(x) for x in db.get_type_word_ids(word_dict["type"], difficulty)]

        if type and not ids:
            words = db.get_words_type(type)
            return render_template(
                "words.html", words=words, type=type, message="No words"
            )
        elif not ids:
            types = db.list_types()
            return render_template("index.html", types=types, message="No words")

        return render_template(
            "word.html", word_dict=word_dict, ids=ids, shuffle_study=shuffle_study
        )

    @login_required
    def update_difficulty(self):
        word_id = request.form.get("word_id")
        word_id = request.json["word_id"]
        difficulty = request.json["difficulty"]

        db.update_difficulty(word_id, int(difficulty))
        return "success", 200

    @login_required
    def add_update_word(self):
        user_id = session["user_id"]
        word_id = request.args.get("word_id")
        word = request.args.get("word", False)
        artikel = request.args.get("artikel", "")
        plural = request.args.get("plural", "")
        type = request.args.get("type")
        sentence = request.args.get("sentence")
        difficulty = request.args.get("difficulty", 1)
        sentence_eng = request.args.get("sentence_eng")
        pronunciation = request.args.get("pronunciation")
        update = request.args.get("update", False)

        if update == "false":
            update = False

        new_word = {
            "word": word,
            "type": type,
            "user_id": ObjectId(user_id),
            "sentence": sentence,
            "sentence_eng": sentence_eng,
            "pronunciation": pronunciation,
            "difficulty": difficulty,
        }

        
        if type == "noun":
            new_word["artikel"] = artikel
            new_word["plural"] = plural

        if word and type:
            db.add_update_word(word_id, new_word, update)

            message = "Updated database"

            if update:
                message = "Updated database"

            if word:
                return (
                    json.dumps({"success": True, "message": message}),
                    200,
                    {"ContentType": "application/json"},
                )
            else:
                return (
                    json.dumps({"success": False, "message": "No word entered"}),
                    400,
                    {"ContentType": "application/json"},
                )

        else:
            types = db.list_types()
            return render_template("index.html", types=types, message="Incorrect input")

    @login_required
    def update_word_redirect(self):
        word_id = request.args.get("word_id")
        word_dict = db.get_word(word_id)
        types = db.list_types()
        return render_template(
            "index.html", types=types, word_dict=word_dict, word_id=word_id, update=True
        )

    @login_required
    def delete_word(self):
        word_id = request.args.get("word_id")
        type = request.args.get("type")
        db.delete_word(word_id)

        words = db.get_words_type(type)
        return render_template("words.html", words=words, type=type)

    @login_required
    def search(self):
        search_term = request.args.get("search_term").lower()
        words = db.search_word(search_term)

        if len(words) > 0:
            return render_template("words.html", words=words, type="Search")
        else:
            types = db.list_types()
            return render_template("index.html", types=types, message="No words")

    @login_required
    def get_words_without_sentence(self):
        words = db.get_words_without_sentence()

        if len(words) > 0:
            return render_template("words.html", words=words, type="Add sentence")
        else:
            types = db.list_types()
            return render_template("index.html", types=types, message="No words")

    @login_required
    def get_counts(self):
        type = request.args.get("type", False)
        counts = db.count_words(type)
        return counts, 200


views = [MainView, WordView, AuthView]
server.register_views(views)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
