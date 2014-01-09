import datetime
import jinja2
import logging
import os
import random
import sha
import webapp2

# App Engine imports.
from google.appengine.ext import ndb
from google.appengine.api import mail

# File imports.
import settings
import models
import mailman

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
    email_input = self.request.get('email', default_value='').encode('utf-8')
    response_code = -1 # unspecified error
    try:
      if models.User.query(models.User.email == email_input).count() > 0:
        raise ValueError('1 Email already in datastore.')
      salt = sha.new(str(random.random())).hexdigest()[:5]
      verification_key = sha.new(salt+email_input).hexdigest()
      user = models.User(email=email_input,
                         verification_key=verification_key)
      user.put()
      mailman.sendVerificationEmail(email_input, verification_key)
      response_code = 0 # success
    except Exception as e:
      logging.exception(e)
      if str(e):
        response_code = str(e)[0] # specific error
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write(response_code) # Response codes:
                                       # -1 = unspecified error
                                       # 0 = success
                                       # 1 = email address already in datastore
                                       # 2 = empty email
                                       # 3 = malformed email

class VerificationPage(webapp2.RequestHandler):

  def get(self):
    key_input = self.request.get('k', default_value='').encode('utf-8')
    email_input = self.request.get('e', default_value='').encode('utf-8')
    message = 'Unknown error.'
    try:
      if not key_input:
        raise ValueError('No verification key provided.')
      if not email_input:
        raise ValueError('No email address provided.')
      user = models.User.query(models.User.email == email_input).fetch(1)[0]
      if not user:
        raise ValueError('User doesn\'t exist.')
      if user.verification_key != key_input:
        raise ValueError('Invalid verification key.')
      if user.verified:
        raise ValueError('User already verified.')
      if (datetime.datetime.now() - user.date).days > 7:
        raise ValueError('Verification code expired.')
      user.verified = True
      user.put()
      message = 'Verfied!'
    except Exception as e:
      logging.exception(e)
      if str(e):
        message = str(e)
    template = JINJA_ENVIRONMENT.get_template('templates/verification.html')
    self.response.write(template.render({'message': message}))

routes = [
  ('/', MainPage),
  ('/signup-form', SignupFormSubmission),
  ('/verify', VerificationPage),
]

application = webapp2.WSGIApplication(routes, debug=settings.DEBUG)