from flask_admin import Admin, AdminIndexView, AdminIndexView
from wtforms import form, fields
from flask_admin.contrib.pymongo import ModelView
from flask import redirect, url_for, session
from flask_admin.menu import MenuLink

#overwrite methods in the class
class ModelView(ModelView):
    def is_accessible(self):
        session_email = session.get("email", None)
        if  session_email and session_email == "gok.asci@gmail.com":
            print("helo")
            return True
            
        else:
            return False

class UserForm(form.Form):
    name = fields.StringField('Name')
    email = fields.StringField('Email')
    password = fields.StringField('Password')
    
class UserView(ModelView):
    column_list = ('name', 'email', 'password')
    form = UserForm


class WordForm(form.Form):
    artikel = fields.StringField('artikel')
    plural = fields.StringField('plural')
    user_id = fields.StringField('user_id')
    pronuncation = fields.StringField('pronuncation')
    artikel = fields.StringField('artikel')
    word = fields.StringField('word')
    type = fields.StringField('type')
    sentence = fields.StringField('sentence')
    sentence_eng = fields.StringField('sentence_eng')

    def is_accessible(self):
        if session["email"] == "gok.asci@gmail.com":
            return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'), message="You don't have permission")



    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'), message="You don't have permission")
    
class WordView(ModelView):
    column_list = ('artikel', 'word', 'type', 'sentence_eng', 'sentence', 'plural', 'pronunciation', 'user_id')
    form = WordForm


class DashboardView(AdminIndexView):

    def is_visible(self):
        # This view won't appear in the menu structure
        return False

class FlaskAdmin:
    def __init__(self, app, db):
        self.admin = Admin(app, name='Admin', url='/admin', template_mode='bootstrap3', index_view=DashboardView())
        self.app = app
        self.db = db

        # add views and links
        self.add_views()
        self.add_links()


    def add_views(self):
        self.admin.add_view(UserView(self.db.users))
        self.admin.add_view(WordView(self.db.words))
    
    def add_links(self):
        self.admin.add_link(MenuLink(name='Back to Main Website', category='', url="/login"))