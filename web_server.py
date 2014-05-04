# Python library imports.
from datetime import datetime 
import jinja2
import json
import logging
import os
import random
import sha
import string
import webapp2
from webapp2_extras import sessions

# App Engine imports.
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import app_identity

# File imports.
from secrets import keys
import mailman
import models
import settings

from apiclient.discovery import build
from oauth2client.appengine import AppAssertionCredentials
from oauth2client.appengine import StorageByKeyName
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from apiclient import errors
from apiclient.http import MediaFileUpload
import httplib2

import atom
import gdata.spreadsheets.client
import gdata.spreadsheet.service
import gdata.client
import gdata.service

CLIENT_SECRETS = json.load(open('secrets/client_secrets.json'))['web']

SCOPES = ['email','https://www.googleapis.com/auth/drive',
          'https://spreadsheets.google.com/feeds']

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Session management logic from
# https://webapp-improved.appspot.com/api/webapp2_extras/sessions.html
class BaseHandler(webapp2.RequestHandler):

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        logging.info('Dispatching.')

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class MainPage(BaseHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        # Create a state token to prevent request forgery.
        # Store it in the session for later validation.
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        self.session['state'] = state
        self.response.write(template.render(
                {'client_id': keys.client_id,
                 'state': state,
                 'application_name': 'Gratitude Reminder',}))


class Signup(BaseHandler):

    def post(self):
        response_code = -1 # unspecified error
        # Ensure that the request is not a forgery and that the user sending
        # this connect request is the expected user.
        if self.request.get('state', '') != self.session['state']:
            response_code = 10
        code = self.request.body
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('secrets/client_secrets.json',
                                                 scope=' '.join(SCOPES))
            oauth_flow.redirect_uri = 'postmessage'
            received_credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            self.response.write('Failed to upgrade the authorization code.')
            self.response.set_status(401)
            return
        # Check that the access token is valid.
        access_token = received_credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            self.response.write(result.get('error'))
            self.response.set_status(500)
            return
        # Verify that the access token is valid for this app.
        if result['issued_to'] != CLIENT_SECRETS['client_id']:
            logging.debug('Token\'s client ID does not match app\'s.')
            self.response.write('Token\'s client ID does not match app\'s.')
            self.response.set_status(401)
            return
        stored_credentials = self.session.get('credentials')
        stored_gplus_id = self.session.get('gplus_id')
        received_gplus_id = result['user_id']
        received_email = result['email']
        response_code = 0 # success
        create_responses_spreadsheet(received_credentials)
        if stored_credentials is not None and
        received_gplus_id == stored_gplus_id:
            logging.debug('Current user is already connected.')
            self.response.write('Current user is already connected.')
            self.response.set_status(200)
            return
        # Store the access token in the session for later use.
        self.session['credentials'] = received_credentials.to_json()
        self.session['gplus_id'] = received_gplus_id
        try:
            if models.User.query(
                models.User.gplus_id == received_gplus_id).count() > 0:
                raise ValueError('User already in datastore.')
            user = models.User(credentials=received_credentials,
                               email=received_email,
                               gplus_id=received_gplus_id)
            user.put()
            mailman.send_welcome(received_email)
        except Exception as e:
            logging.exception(e)
            if str(e):
                response_code = str(e)[0] # specific error
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(response_code)


class BlessingsPage(webapp2.RequestHandler):

    def get(self):
        key_input = self.request.get('k', default_value='').encode('utf-8')
        email_input = self.request.get('e', default_value='').encode('utf-8')
        try:
            user = retrieve_user(key_input, email_input)
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


def retrieve_user(key, email):
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
    ('/signup', Signup),
    ('/blessings', BlessingsPage),
    ]

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': keys.session,
    }

app = webapp2.WSGIApplication(routes, debug=settings.DEBUG, config=config)
