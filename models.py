# App Engine imports.
from google.appengine.ext import ndb


class User(ndb.Model):
  email = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)

