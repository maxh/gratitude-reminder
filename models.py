# App Engine imports.
from google.appengine.ext import ndb


class User(ndb.Model):
  
  def emailValidator(prop, value):
    if not value:
      raise ValueError('2 Empty email address.')
    if value.find('@') == -1 or value.find('.') == -1:
      raise ValueError('3 Malformed email address.')
    return value.lower().strip()

  email = ndb.StringProperty(validator=emailValidator)
  verified = ndb.BooleanProperty(default=False)
  date = ndb.DateTimeProperty(auto_now_add=True)
