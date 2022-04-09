from flask_admin import Admin, AdminIndexView, AdminIndexView
from wtforms import form, fields
from flask_admin.contrib.pymongo import ModelView
from flask import redirect, url_for, session
from flask_admin.menu import MenuLink

# overwrite methods in the class
class ModelView(ModelView):
    def is_accessible(self):
        if session.get("admin", False) == True:
            return True
        else:
            return False


class UserForm(form.Form):
    first_name = fields.StringField("first_name")
    last_name = fields.StringField("last_name")
    username = fields.StringField("username")
    email = fields.StringField("email")
    admin = fields.BooleanField("admin")
    

class UserView(ModelView):
    column_list = ("first_name", "last_name", "username", "admin", "email")
    form = UserForm


class WordForm(form.Form):
    artikel = fields.StringField("artikel")
    plural = fields.StringField("plural")
    pronuncation = fields.StringField("pronuncation")
    artikel = fields.StringField("artikel")
    word = fields.StringField("word")
    type = fields.StringField("type")
    sentence = fields.StringField("sentence")
    sentence_eng = fields.StringField("sentence_eng")
    difficulty = fields.IntegerField("difficulty")
    verb_tenses = fields.IntegerField("verb_tenses")

    def is_accessible(self):
        if session.get("admin", False) == True:
            return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('AuthView:login_auth'), message="You don't have permission")


class WordView(ModelView):
    
    column_searchable_list = ['word', 'type']
    # column_filters = ['admin', 'confirm email']
    page_size = 50

    column_list = (
        "artikel",
        "word",
        "difficulty",
        "type",
        "sentence",
        "sentence_eng",
        "plural",
        "pronunciation",
        "last_diff_update",
        "verb_tenses",
    )
    form = WordForm


class DashboardView(AdminIndexView):
    def is_visible(self):
        # This view won't appear in the menu structure
        return False


class FlaskAdmin:
    def __init__(self, app, db):
        self.admin = Admin(
            app,
            name="Admin",
            url="/admin",
            template_mode="bootstrap3",
            index_view=DashboardView(),
        )
        self.app = app
        self.db = db

        # add views and links
        self.add_views()
        self.add_links()

    def add_views(self):
        self.admin.add_view(UserView(self.db.users))
        self.admin.add_view(WordView(self.db.words))

    def add_links(self):
        self.admin.add_link(
            MenuLink(name="Back to Main Website", category="", url="/auth/login")
        )
