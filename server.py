# Python imports.
import datetime
import jinja2
import os
import webapp2
import logging

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
    email_input = self.request.get('email', default_value='')
    response_code = 0 # success
    try:
      if models.User.query(models.User.email == email_input).count() > 0:
        raise ValueError('1 Email already in datastore.')
      user = models.User(email=email_input)
      user.put()
    except Exception as e:
      logging.exception(e)
      response_code = str(e)[0] 
    self.response.write(response_code) # Response codes:
                                       # 0 = success
                                       # 1 = email address already in datastore
                                       # 2 = empty email
                                       # 3 = malformed email


routes = [
  ('/', MainPage),
  ('/signup-form', SignupFormSubmission),
  ('/confim', SignupFormSubmission),
]

application = webapp2.WSGIApplication(routes, debug=settings.DEBUG)