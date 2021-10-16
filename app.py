from flask import Flask, request, render_template, redirect

from flask_classful import FlaskView
from dotenv import load_dotenv

from classes.s3 import S3

app = Flask(__name__, template_folder="templates")

# load variables
load_dotenv(".env")
# app config
app.config["JSON_AS_ASCII"] = False

s3 = S3()
DATA = s3.get_source_json()

@app.route("/")
def starting_url():
    return redirect("/type")


@app.route("/update")
def update_json():
    global DATA
    DATA = s3.get_source_json()
    return redirect("/type")

class TypeView(FlaskView):
        
    def index(self):
        types = DATA.keys()
        return render_template("types.html", types=types)
        

class WordView(FlaskView):
    
    def list(self):
        type = request.args.get("type").lower()
        words = DATA[type].keys()
        return render_template("words.html", words=words, type=type)  #

    def incr_request_count(self, type, word):
        """
        increase the request count by one
        """
        DATA[type][word]["request_count"] += 1

        s3.update_source_json(DATA)

    def get_word(self):
        word = request.args.get("word").lower()
        type = request.args.get("type").lower()

        word_dict = DATA[type][word]

        #self.incr_request_count(type, word)

        return render_template("word.html", word_dict=word_dict, type=type)

    def add_update_word(self):
        word = request.args.get("word").lower()
        type = request.args.get("type").lower()
        english = request.args.get("english")
        sentence = request.args.get("sentence")
        sentence_eng = request.args.get("sentence_eng")

        new_word = {
           "word": word ,
           "english": english,
           "sentence": sentence,
           "sentence_eng": sentence_eng
        }

        if word and type:
            current_data = s3.get_source_json()
            current_data[type][word] = new_word
            s3.update_source_json(current_data)
            word_dict = current_data[type][word]
            return render_template("word.html", word_dict=word_dict, type=type)
        else:
            types = DATA.keys()
            return render_template("types.html", types=types, message="Incorrect input")
        

    def search(self):
        word_input = request.args.get("word").lower()

        all_words_dict = {}

        for key in DATA.keys():

            for word in DATA[key]:
                all_words_dict[word] = DATA[key][word]

        try:
            word_dict = all_words_dict[word_input]
            return render_template("word.html", word_dict=word_dict, type=type)
        except KeyError:
            types = DATA.keys()
            return render_template("types.html", types=types, message="No words")


s3 = S3()

TypeView.register(app)
WordView.register(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
