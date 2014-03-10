from datetime import datetime 
import jinja2
import logging
import os
import random
import sha
import webapp2

# App Engine imports.
from google.appengine.ext import ndb

# File imports.
import mailman
import models
import settings

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
      mailman.sendVerification(email_input, verification_key)
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
      user = retrieveUser(key_input, email_input)
      if user.verified:
        raise ValueError('User already verified.')
      if (datetime.now() - user.date).days > 7:
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


class BlessingsPage(webapp2.RequestHandler):
  def get(self):
    key_input = self.request.get('k', default_value='').encode('utf-8')
    email_input = self.request.get('e', default_value='').encode('utf-8')
    try:
      user = retrieveUser(key_input, email_input)
      parent_key = ndb.Key(models.User, user.email).get()
      blessings = models.Blessing.query(ancestor=parent_key).order(
        -models.Blessing.date)
      template = JINJA_ENVIRONMENT.get_template('templates/blessings.html')
      self.response.write(template.render({'blessings': blessings}))
    except Exception as e:
      logging.exception(e)
      if str(e):
        error = str(e)
      else:
        error = 'Unknown error :('
      template = JINJA_ENVIRONMENT.get_template('templates/error.html')
      self.response.write(template.render({'error': error}))


def retrieveUser(key, email):
  if not key:
    raise ValueError('No verification key provided.')
  if not email:
    raise ValueError('No email address provided.')
  user = models.User.query(models.User.email == email).fetch(1)[0]
  if not user:
    raise ValueError('User doesn\'t exist.')
  if user.verification_key != key:
    raise ValueError('Invalid verification key.')
  return user


routes = [
  ('/', MainPage),
  ('/signup-form', SignupFormSubmission),
  ('/verify', VerificationPage),
  ('/blessings', BlessingsPage),
]

app = webapp2.WSGIApplication(routes, debug=settings.DEBUG)
