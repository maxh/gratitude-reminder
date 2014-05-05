""" web.py:
    Handles incoming requests from web users.
"""

# Python library imports.
from datetime import datetime
import jinja2
import json
import logging
import os
import webapp2

# App Engine imports.
from google.appengine.ext import ndb
from google.appengine.api import users

# File imports.
from secrets import keys
import drive
import link
import mail
import models
import settings


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.dirname(__file__) + '/templates/web/'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        user = users.get_current_user()
        if user:
            users_db = models.User.query(models.User.email == user.email()).fetch(1)
            if len(users_db) == 0:
                raise Exception('Email address not in our database.')
            user_db = users_db[0]
            self.response.write(template.render(
                signed_in=True,
                user_email=user_db.email,
                sign_out_url=users.create_logout_url('/'),
                responses_link=link.spreadsheet(user_db.file_id),
                unsubscribe_link=link.unsubscribe(user_db.email)))
        else:
            self.response.write(template.render(
                signed_in=False,
                sign_up_link=users.create_login_url('/signup'),
                sign_in_link=users.create_login_url('/')))



class Signup(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        email = user.email()
        try:
            if models.User.query(models.User.email == email).count() > 0:
                raise Exception('User is already signed up!')
            file_id = drive.create_responses_spreadsheet(email)
            user = models.User(email=email, file_id=file_id)
            user.put()
            mail.send_email_from_template(email, file_id, 'welcome')
        except Exception as e:
            logging.exception(e)
        self.redirect("/")


class Unsubscribe(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            email = user.email()
        else:
            email = self.request.get('email')
        try:
            if not email:
                raise Exception('No email specified.')
            users = models.User.query(models.User.email == email).fetch(1)
            if len(users) == 0:
                raise Exception('Email address not in our database.')
            user = users[0]
            if user.unsubscribe_date:
                raise Exception('User already unsubscribed.')
            user.unsubscribed = True
            user.put()
            mail.send_email_from_template(email, file_id, 'unsubscribe')
        except Exception as e:
            logging.exception(e)
        self.response.write("Successfully unsubscribed.")


routes = [
    ('/', MainPage),
    ('/signup', Signup),
    ('/unsubscribe', Unsubscribe),
]

app = webapp2.WSGIApplication(routes, debug=settings.DEBUG)
