# Python library imports.
from datetime import datetime 
import jinja2
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

# File imports.
import keys
import mailman
import models
import settings

#
import sys
sys.path.append('./lib')
import oauth2client.client

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


class SignupFormSubmission(BaseHandler):

    def post(self):
        response_code = -1 # unspecified error
        # Ensure that the request is not a forgery and that the user sending
        # this connect request is the expected user.
        if self.request.get('state', '') != self.session['state']:
            response_code = 10

        logging.info('Now calling in to connect to G+.')
        gPlusSigninFlow(self.request)
        user = users.get_current_user()
        email_input = user.email()
        
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
            message = 'Verifed!'
        except Exception as e:
            logging.exception(e)
            if str(e):
                message = str(e)
        template = JINJA_ENVIRONMENT.get_template(
                    'templates/verification.html')
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


def gPlusSigninFlow(request):
    gplus_id = request.get('gplus_id')
    code = request.body
    logging.info('Now connecting to G+.')
    
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        self.response.write('Failed to upgrade the authorization code.')
        self.response.set_status(401)
        return
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        self.response.write(result.get('error'))
        self.response.set_status(500)
        return
    # Verify that the access token is used for the intended user.
    if result['user_id'] != gplus_id:
        self.response.write('Token\'s user ID doesn\'t match given user ID.')
        self.response.set_status(401)
        return
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        self.response.write('Token\'s client ID does not match app\'s.')
        self.response.set_status(401)
        return
    stored_credentials = self.session.get('credentials')
    stored_gplus_id = self.session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        self.response.write('Current user is already connected.')
        self.response.set_status(200)
        return response
    # Store the access token in the session for later use.
    self.session['credentials'] = credentials
    self.session['gplus_id'] = gplus_id
    self.response.write('Successfully connected user.')
    self.response.set_status(200)


routes = [
    ('/', MainPage),
    ('/signup-form', SignupFormSubmission),
    ('/verify', VerificationPage),
    ('/blessings', BlessingsPage),
    ]

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': keys.session,
    }
app = webapp2.WSGIApplication(routes, debug=settings.DEBUG, config=config)
