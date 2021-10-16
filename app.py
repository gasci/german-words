#%%
from flask import request, render_template, redirect

from flask_classful import FlaskView
from classes.mongo import Database
from classes.app import App

app = App().init
db = Database(".env")


@app.route("/")
def starting_url():
    return redirect("/main")


class MainView(FlaskView):
    def index(self):
        types = db.list_types()
        return render_template("main.html", types=types)


class WordView(FlaskView):
    def list(self):
        type = request.args.get("type").lower()
        words = db.get_words_type(type)
        return render_template("words.html", words=words, type=type)  #

    def get_word(self):
        word_id = request.args.get("word_id")
        word_dict = db.get_word(word_id)
        return render_template("word.html", word_dict=word_dict)

    def add_update_word(self):
        word_id = request.args.get("word_id")
        word = request.args.get("word")
        type = request.args.get("type")
        sentence = request.args.get("sentence")
        sentence_eng = request.args.get("sentence_eng")

        new_word = {
            "word": word,
            "type": type,
            "sentence": sentence,
            "sentence_eng": sentence_eng,
        }

        types = db.list_types()

        if word and type:
            db.add_update_word(word_id, new_word)
            return render_template("main.html", types=types, message="Updated database")
        else:
            
            return render_template("main.html", types=types, message="Incorrect input")

    def update_word_redirect(self):
        word_id = request.args.get("word_id")
        word_dict = db.get_word(word_id)
        types = db.list_types()
        return render_template(
            "main.html", types=types, word_id=word_id, word_dict=word_dict
        )

    def delete_word(self):
        word_id = request.args.get("word_id")
        type = request.args.get("type")

        db.delete_word(word_id)

        words = db.get_words_type(type)
        return render_template("words.html", words=words, type=type)

    def search(self):
        word = request.args.get("word").lower()

        result = db.search_word(word)

        if len(result) > 0:
            word_dict = result
            return render_template("word.html", word_dict=word_dict)
        else:
            types = db.list_types()
            return render_template("main.html", types=types, message="No words")


MainView.register(app)
WordView.register(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0")

# %%
