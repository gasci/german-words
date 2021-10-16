#%%
from flask import Flask, request, render_template, redirect

from flask_classful import FlaskView

from classes.mongo import Database

app = Flask(__name__, template_folder="templates")

# app config
app.config["JSON_AS_ASCII"] = False

db = Database(".env")
#%%


@app.route("/")
def starting_url():
    return redirect("/type")


class TypeView(FlaskView):
    def index(self):
        types = db.list_colls()
        return render_template("types.html", types=types)


class WordView(FlaskView):
    def list(self):
        type = request.args.get("type").lower()
        words = db.data[type].distinct("word")
        return render_template("words.html", words=words, type=type)  #

    # def incr_request_count(self, type, word):
    #     """
    #     increase the request count by one
    #     """
    #     DATA[type][word]["request_count"] += 1

    #     s3.update_source_json(DATA)

    def get_word(self):
        word = request.args.get("word").lower()
        type = request.args.get("type").lower()

        word_dict = db.get_word(type, word)

        # self.incr_request_count(type, word)

        return render_template("word.html", word_dict=word_dict, type=type)

    def add_update_word(self):
        word = request.args.get("word").lower()
        type = request.args.get("type").lower()
        english = request.args.get("english")
        sentence = request.args.get("sentence")
        sentence_eng = request.args.get("sentence_eng")

        new_word = {
            "word": word,
            "english": english,
            "sentence": sentence,
            "sentence_eng": sentence_eng,
        }

        if word and type and english:
            db.add_update_word(type, new_word)
            return render_template("word.html", word_dict=new_word, type=type)
        else:
            types = db.list_colls()
            return render_template("types.html", types=types, message="Incorrect input")

    def update_word(self):
        word = request.args.get("word").lower()
        type = request.args.get("type").lower()

        word_dict = db.get_word(type, word)

        types = db.list_colls()
        return render_template("types.html", types=types, word_dict=word_dict)

    def delete_word(self):
        word = request.args.get("word").lower()
        type = request.args.get("type").lower()

        db.delete_word(type, word)

        words = db.data[type].distinct("word")
        return render_template("words.html", words=words, type=type)

    def search(self):
        word = request.args.get("word").lower()
        
        result = db.search_word(word)

        if len(result) > 0:
            word_dict = result
            return render_template("word.html", word_dict=word_dict, type=type)
        else:        
            types = db.list_colls()
            return render_template("types.html", types=types, message="No words")


TypeView.register(app)
WordView.register(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0")

# %%
