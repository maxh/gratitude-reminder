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
import drive_manager
import mailman
import models
import settings


CLIENT_SECRETS = json.load(open('secrets/client_secrets.json'))['web']

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        user = users.get_current_user()
        if user:
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
            user_db = models.User.query(models.User.email == user.email()).fetch(1)[0]
            logging.info(user_db.file_id)
            drive_manager.add_gratitude_response(user_db.file_id, 'This is a test.',
                                         datetime.today().strftime('%Y-%m-%d'))
        else:
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/signup'))
        self.response.write(template.render({'content': greeting}))


class Signup(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        email = user.email()
        try:
            if models.User.query(models.User.email == email).count() > 0:
                logging.info('User is already signed up!')
                raise ValueError
                #self.response.write('Looks like you are already signed up!')
            file_id = drive_manager.create_responses_spreadsheet(email)
            user = models.User(email=email, file_id=file_id)
            user.put()
            # Purely for testing.
            mailman.send_welcome(email,
                                 drive_manager.generate_web_link(file_id))
        except Exception as e:
            logging.exception(e)
        self.redirect("/")


routes = [
    ('/', MainPage),
    ('/signup', Signup),
    ]

app = webapp2.WSGIApplication(routes, debug=settings.DEBUG)
