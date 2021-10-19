#%%
from flask import request, render_template, redirect, session, url_for
from flask_classful import FlaskView, route


from classes.mongo import Database
from classes.server import Server
from classes.admin import FlaskAdmin

from bson.objectid import ObjectId
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
    return redirect(url_for('AuthView:login_auth'))


class AuthView(FlaskView):

    @route('/register', methods=['GET', 'POST'])
    def register_auth(self):
        
        if not can_register == "True":
            message = (
                "Currently, registration is not allowed. Contact: drgoktugasci@gmail.com"
            )
            return render_template("auth/login.html", message=message)

        message = "Please register"
        server.is_authenticated_check()
        if "email" in session:
            return redirect(url_for("MainView:index"))
        if request.method == "POST":

            user = request.form.get("fullname")
            email = request.form.get("email")

            password1 = request.form.get("password1")
            password2 = request.form.get("password2")

            user_found = db.users.find_one({"name": user})
            email_found = db.users.find_one({"email": email})
            if user_found:
                message = "There already is a user by that name"
                return render_template("auth/register.html", message=message)
            if email_found:
                message = "This email already exists in database"
                return render_template("auth/register.html", message=message)
            if password1 != password2:
                message = "Passwords should match!"
                return render_template("auth/register.html", message=message)
            else:
                hashed = bcrypt.hashpw(password2.encode("utf-8"), bcrypt.gensalt())
                user_input = {"name": user, "email": email, "password": hashed}
                db.users.insert_one(user_input)

                user_data = db.users.find_one({"email": email})
                new_email = user_data["email"]
                session["email"] = user_data["email"]
                session["user_id"] = str(user_data["_id"])
                server.is_authenticated_check()
                return render_template("index.html", email=new_email)
        return render_template("auth/register.html")

    @route('/login', methods=['GET', 'POST'])
    def login_auth(self):
        
        message = ""
        server.is_authenticated_check()
        if "email" in session:
            return redirect(url_for("MainView:index"))

        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            user_data = db.users.find_one({"email": email})
            if user_data:
                email_val = user_data["email"]
                passwordcheck = user_data["password"]

                if bcrypt.checkpw(password.encode("utf-8"), passwordcheck):
                    session["email"] = email_val
                    session["user_id"] = str(user_data["_id"])
                    server.is_authenticated_check()
                    return redirect(url_for("MainView:index"))
                else:
                    message = "Wrong password"
                    return render_template("auth/login.html", message=message)

            else:
                message = "Email not found"
                return render_template("auth/login.html", message=message)
        return render_template("auth/login.html", message=message)

    @route('/logout', methods=['GET', 'POST'])
    def logout_auth(self):
        
        session.pop("email", None)
        session.pop("user_id", None)
        server.is_authenticated_check()
        return render_template("auth/login.html")


class MainView(FlaskView):

    default_methods = ["GET", "POST"]

    def index(self):

        if "email" not in session:
            return redirect(url_for('AuthView:login_auth'))

        types = db.list_types()
        return render_template("index.html", types=types)


class WordView(FlaskView):

    default_methods = ["GET", "POST"]

    def list(self):

        if "email" not in session:
            return redirect(url_for('AuthView:login_auth'))

        type = request.args.get("type").lower()
        words = db.get_words_type(type)
        return render_template("words.html", words=words, type=type)

    def get_word(self):

        if "email" not in session:
            return redirect(url_for('AuthView:login_auth'))

        word_id = request.args.get("word_id", False)
        type = request.args.get("type", False)
        shuffle_study = request.args.get("shuffle_study", False)
        shuffle_words = request.args.get("shuffle_words", False)

        if shuffle_study:
            shuffle_study = True

        if shuffle_words:
            shuffle_words = True

        # print(shuffle_study)
        # print(shuffle_words)

        if shuffle_words and shuffle_study:
            # print("shuffled")
            ids = [str(x) for x in db.get_type_word_ids(type)]
            shuffle(ids)
            # print(ids)
            session["word_ids"] = ids
            word_id = ids[0]
            word_dict = db.get_word(word_id)
        elif not shuffle_words and shuffle_study:
            # print("not shuffled")
            word_dict = db.get_word(word_id)
            ids = session["word_ids"]
            # print(ids)
        else:
            word_dict = db.get_word(word_id)
            ids = [str(x) for x in db.get_type_word_ids(word_dict["type"])]

        return render_template(
            "word.html", word_dict=word_dict, ids=ids, shuffle_study=shuffle_study
        )

    def add_update_word(self):

        if "email" not in session:
            return redirect(url_for('AuthView:login_auth'))

        word_id = request.args.get("word_id")
        user_id = session["user_id"]
        word = request.args.get("word")
        artikel = request.args.get("artikel", "")
        plural = request.args.get("plural", "")
        type = request.args.get("type")
        sentence = request.args.get("sentence")
        sentence_eng = request.args.get("sentence_eng")
        pronunciation = request.args.get("pronunciation")

        new_word = {
            "word": word,
            "type": type,
            "user_id": ObjectId(user_id),
            "sentence": sentence,
            "sentence_eng": sentence_eng,
            "pronunciation": pronunciation,
        }

        if type == "noun":
            new_word["artikel"] = artikel
            new_word["plural"] = plural

        if word and type:
            db.add_update_word(word_id, new_word)
            types = db.list_types()
            return render_template(
                "index.html",
                types=types,
                message="Updated database",
            )
        else:
            types = db.list_types()
            return render_template("index.html", types=types, message="Incorrect input")

    def update_word_redirect(self):

        if "email" not in session:
            return redirect(url_for('AuthView:login_auth'))

        word_id = request.args.get("word_id")
        word_dict = db.get_word(word_id)
        types = db.list_types()
        return render_template(
            "index.html", types=types, word_dict=word_dict, word_id=word_id
        )

    def delete_word(self):

        if "email" not in session:
            return redirect(url_for('AuthView:login_auth'))

        word_id = request.args.get("word_id")
        type = request.args.get("type")

        db.delete_word(word_id)

        words = db.get_words_type(type)
        return render_template("words.html", words=words, type=type)

    def search(self):

        if "email" not in session:
            return redirect(url_for('AuthView:login_auth'))

        word = request.args.get("word").lower()
        result = db.search_word(word)

        if len(result) > 0:
            word_dict = result
            ids = [str(x) for x in db.get_type_word_ids(word_dict["type"])]
            return render_template("word.html", word_dict=word_dict, ids=ids)
        else:
            types = db.list_types()
            return render_template("index.html", types=types, message="No words")


views = [MainView, WordView, AuthView]
server.register_views(views)


if __name__ == "__main__":
    app.run(host="0.0.0.0")

# %%
