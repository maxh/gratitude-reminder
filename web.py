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
        # User just registered, needs to appear first in control in case user
        # hasn't been stored in DB yet. Also, we can respond faster without
        # having to wait for DB response.
        if (self.request.get('sup') == 'just_registered'):
            self.response.write(template.render(
                user_status='just_registered',
                user_email=user.email()))
            return
        if user:
            users_db = models.User.query(
                models.User.email == user.email()).fetch(1)
        # User either isn't signed in or is signed in but isn't registered.
        if not user or len(users_db) == 0:
            self.response.write(template.render(
                user_status='signed_out_or_not_registered',
                sign_up_link=users.create_login_url('/register'),
                sign_in_link=users.create_login_url('/')))
            return
        if self.request.get('sup') == 'already_registered':
            status = 'already_registered'
        else:
            status = 'registered'
        user_db = users_db[0]
        self.response.write(template.render(
            user_status=status,
            user_email=user_db.email,
            sign_out_link=users.create_logout_url('/'),
            responses_link=link.spreadsheet(user_db.file_id),
            unsubscribe_link=link.unsubscribe(user_db.email)))



class Register(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        email = user.email()
        try:
            if len(models.User.query(models.User.email == email).fetch(1)) == 1:
                self.redirect("/?sup=already_registered")
                return
            file_id = drive.create_responses_spreadsheet(email)
            user = models.User(email=email, file_id=file_id)
            user.put()
            mail.send_email_from_template(email, file_id, 'welcome')
        except Exception as e:
            logging.exception(e)
        self.redirect("/?sup=just_registered")


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
            users_db = models.User.query(models.User.email == email).fetch(1)
            if len(users_db) == 0:
                raise Exception('Email address not in our database.')
            user = users_db[0]
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
    ('/register', Register),
    ('/unsubscribe', Unsubscribe),
]

app = webapp2.WSGIApplication(routes, debug=settings.DEBUG)
