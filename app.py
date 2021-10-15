from flask import Flask, jsonify, request, render_template, redirect
import json
from flask_classful import FlaskView
from dotenv import load_dotenv
import os

app = Flask(__name__, template_folder='templates')

# HOME = os.environ['CLUSTER_USERNAME']
# CLUSTER_PASSWORD = os.environ['CLUSTER_USERNAME']

# print(HOME)
# print(CLUSTER_PASSWORD)

# load variables
load_dotenv(".env")
# app config
app.config['JSON_AS_ASCII'] = False

@app.route("/")
def starting_url():
    return redirect("/type")


class TypeView(FlaskView):
    def __init__(self):
        with open("assets/vocab.json", "r", encoding="utf-8") as json_file:
            self.data = json.load(json_file)
    
    def index(self):
        types = self.data.keys()
        return render_template('types.html', types=types)


class WordView(FlaskView):
    def __init__(self):
        with open("assets/vocab.json", "r", encoding="utf-8") as json_file:
            self.data = json.load(json_file)
  
    def list(self):
        type = request.args.get("type")
        words = self.data[type].keys()
        print(words)
        return render_template('words.html', words=words, type=type) #

    def incr_request_count(self, word):
        """
        increase the request count by one
        """
        self.data[word]["request_count"] += 1
    
    def get_word(self):
        word = request.args.get("word")
        type = request.args.get("type")
        
        word_dict = self.data[type][word]

        return render_template('word.html', word_dict=word_dict, type=type ) 

    def search(self):
        word = request.args.get("word")
        
        words_list = {}

        for key in self.data.keys():
            words_list.append(self.data[key])

        word_dict = words_list[word]

        return render_template('word.html', word_dict=word_dict, type=type) 


TypeView.register(app)
WordView.register(app)

if __name__ == "__main__":
  app.run(host='0.0.0.0')