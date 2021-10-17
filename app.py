#%%
from flask import request, render_template, redirect, session, url_for
from flask_classful import FlaskView

from classes.mongo import Database
from classes.server import Server

from bson.objectid import ObjectId
import bcrypt
import os
from random import shuffle
# import asyncio

server = Server()
app = server.app
db = Database(".env")
word_ids = None

can_register = os.environ.get("CAN_REGISTER")

@app.route("/", methods=['post', 'get'])
def starting_url():
    return redirect(url_for('login'))


@app.route("/register", methods=['post', 'get'])
def register():

    if not can_register == "True":
        message = 'Currently, registration is not allowed. Contact: drgoktugasci@gmail.com'
        return render_template('auth/login.html', message=message)


    message = 'Please register'
    server.is_authenticated_check(session)
    if "email" in session:
        return redirect(url_for('MainView:index', session=session))
    if request.method == "POST":
        
        user = request.form.get("fullname")
        email = request.form.get("email")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = db.users.find_one({"name": user})
        email_found = db.users.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('auth/register.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('auth/register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('auth/register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            db.users.insert_one(user_input)
            
            user_data = db.users.find_one({"email": email})
            new_email = user_data['email']
            session["email"] = user_data['email']
            session["user_id"] = str(user_data['_id'])
            server.is_authenticated_check(session)
            return render_template('index.html', email=new_email, session=session)
    return render_template('auth/register.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = ''
    server.is_authenticated_check(session)
    if "email" in session:
        return redirect(url_for('MainView:index', session=session))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_data = db.users.find_one({"email": email})
        if user_data:
            email_val = user_data['email']
            passwordcheck = user_data['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                session["user_id"] = str(user_data['_id'])
                server.is_authenticated_check(session)
                return redirect(url_for('MainView:index', session=session))
            else:
                message = 'Wrong password'
                return render_template('auth/login.html', message=message)
                    
        else:
            message = 'Email not found'
            return render_template('auth/login.html', message=message)
    return render_template('auth/login.html', message=message)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("email", None)
    session.pop("user_id", None)
    server.is_authenticated_check(session)
    return render_template("auth/login.html")


class MainView(FlaskView):
    def index(self):

        if "email" not in session:
            return redirect(url_for('login'))

        types = db.list_types(session)
        return render_template("index.html", types=types, session=session)


class WordView(FlaskView):
    def __init__(self):
        self.word_ids = None

    def list(self):

        if "email" not in session:
            return redirect(url_for('login'))

        type = request.args.get("type").lower()
        words = db.get_words_type(session, type)
        return render_template("words.html", words=words, type=type, session=session)

    def get_word(self):

        if "email" not in session:
            return redirect(url_for('login'))

        word_id = request.args.get("word_id")
        shuffle_words = request.args.get("shuffle_words", None)
        word_dict = db.get_word(session, word_id)

        print(shuffle_words)

        if shuffle_words == "False" and self.word_ids:
            print("not shuffled")
            ids = self.word_ids
            print(ids)
        else:
            print("shuffled")
            ids = [str(x) for x in db.get_type_word_ids(session, word_dict["type"])]
            shuffle(ids)
            self.word_ids = ids
            print(ids)    
            

        return render_template("word.html", word_dict=word_dict, ids=ids, session=session, study_mode=True)

    def add_update_word(self):

        if "email" not in session:
            return redirect(url_for('login'))

        word_id = request.args.get("word_id")
        user_id = session["user_id"]
        word = request.args.get("word")
        artikel = request.args.get("artikel", None)
        type = request.args.get("type")
        sentence = request.args.get("sentence")
        sentence_eng = request.args.get("sentence_eng")

        new_word = {
            "word": word,
            "type": type,
            "user_id": ObjectId(user_id),
            "sentence": sentence,
            "sentence_eng": sentence_eng,
        }

        if type == "noun":
            new_word["artikel"] = artikel

        if word and type:
            db.add_update_word(session, word_id, new_word)
            types = db.list_types(session)
            words = db.get_words_type(session, type)
            return render_template("words.html", words=words, type=new_word["type"], session=session, message="Updated database")
        else:
            types = db.list_types(session)
            return render_template("index.html", types=types, message="Incorrect input", session=session)

    def update_word_redirect(self):

        if "email" not in session:
            return redirect(url_for('login'))

        word_id = request.args.get("word_id")
        word_dict = db.get_word(session, word_id)
        types = db.list_types(session)
        return render_template(
            "index.html", types=types, word_id=word_id, word_dict=word_dict, session=session
        )

    def delete_word(self):

        if "email" not in session:
            return redirect(url_for('login'))

        word_id = request.args.get("word_id")
        type = request.args.get("type")

        db.delete_word(session, word_id)

        words = db.get_words_type(session, type)
        return render_template("words.html", words=words, type=type, session=session)

    def search(self):

        if "email" not in session:
            return redirect(url_for('login'))

        word = request.args.get("word").lower()
        result = db.search_word(session, word)

        if len(result) > 0:
            word_dict = result
            ids = [str(x) for x in db.get_type_word_ids(session, word_dict["type"])]
            return render_template("word.html", word_dict=word_dict, ids=ids, session=session, study_mode=False)
        else:
            types = db.list_types(session)
            return render_template("index.html", types=types, message="No words", session=session)


MainView.register(app)
WordView.register(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0")

# %%
