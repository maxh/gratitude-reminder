# App Engine imports.
import sys
sys.path.append('./lib')
from google.appengine.ext import ndb
from oauth2client.appengine import CredentialsNDBProperty

class User(ndb.Model):

  def emailValidator(prop, value):
    if not value:
      raise ValueError('2 Empty email address.')
    if value.find('@') == -1 or value.find('.') == -1:
      raise ValueError('3 Malformed email address.')
    return value.lower().strip()

  credentials = CredentialsNDBProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)
  email = ndb.StringProperty(validator=emailValidator)
  gplus_id = ndb.StringProperty()
  verification_key = ndb.TextProperty()
  verified = ndb.BooleanProperty(default=False)


class Blessing(ndb.Model):

  content = ndb.TextProperty()
  date = ndb.DateTimeProperty()
