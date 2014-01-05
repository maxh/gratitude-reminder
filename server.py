# Python imports.
import datetime
import jinja2
import os
import webapp2

# App Engine imports.
from google.appengine.ext import ndb

# File imports.
import settings
import models

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render())


class SignupFormSubmission(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'

        email_input = self.request.get('email',default_value='')
        if (not email_input):
            self.response.write("No email received by backend.")
        elif (models.User.query(models.User.email == email_input).fetch(1)):
            self.response.write("That email is already in the datastore.")
        else:
            user = models.User(email=email_input)
            user.put()
            self.response.write("Request to add email sent to datastore.")

routes = [
    ('/', MainPage),
    ('/signup-form', SignupFormSubmission),
]

application = webapp2.WSGIApplication(routes, debug=settings.DEBUG)