from flask import Flask
from urllib.parse import quote_plus

class App:
    def __init__(self):
        self.init = Flask(__name__, template_folder="../templates")

        # app config
        self.init.config["JSON_AS_ASCII"] = False
        self.init.jinja_env.filters["word_background"] = lambda var_list: self.word_background_fixer(var_list)
        self.init.jinja_env.filters["word_text_color"] = lambda var_list: self.word_text_color_fixer(var_list)

    def word_background_fixer(self, var_list):
        if var_list[1] == "noun":

            color_dic = {
                "der": "bg-primary",
                "die": "bg-danger",
                "das": "bg-secondary"
            }

            value = color_dic.get(var_list[0][0:3], None)

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