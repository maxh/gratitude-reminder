# App Engine imports.

from google.appengine.ext import ndb


class User(ndb.Model):

  def emailValidator(prop, value):
    if not value:
      raise ValueError('Empty email address.')
    if value.find('@') == -1 or value.find('.') == -1:
      raise ValueError('Malformed email address.')
    return value.lower().strip()

  date = ndb.DateTimeProperty(auto_now_add=True)
  email = ndb.StringProperty(validator=emailValidator)
  file_id = ndb.StringProperty()
