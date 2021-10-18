from flask import Flask, session

import os

class Server:
    def __init__(self):
        self.app = Flask(__name__, template_folder="../templates")
        self.app.secret_key = os.environ.get("FLASK_SECRET_KEY")
        self.is_authenticated = False
        
        # app config
        self.app.config["JSON_AS_ASCII"] = False
        self.app.jinja_env.filters["word_background"] = lambda var_list: self.word_background_fixer(var_list)
        self.app.jinja_env.filters["word_text_color"] = lambda var_list: self.word_text_color_fixer(var_list)
        self.app.jinja_env.filters["str"] = lambda u: str(u)
        self.app.jinja_env.filters["len"] = lambda u: len(u)
    

    def word_background_fixer(self, var_list):
        if var_list[1] == "noun":

            color_dic = {
                "der": "bg-primary",
                "die": "bg-danger",
                "das": "bg-secondary"
            }

            value = color_dic.get(var_list[0], None)

            if value:
                return value
            else:
                return ""
        else:
            return ""

    def word_text_color_fixer(self, type):
        if type == "noun":
            return "text-white"
        else:
            return "text-black"


    def is_authenticated_check(self):
        if "email" in session:
            self.is_authenticated = True
        else:
            self.is_authenticated = False
            