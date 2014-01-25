import datetime
import logging
import webapp2

# App Engine imports.
from google.appengine.ext import ndb
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

# File imports.
import mailman
import models
import settings


class SendReminderEmails(webapp2.RequestHandler):
  def get(self):
    users = models.User.query().fetch()
    for user in users:
      mailman.sendReminder(user.email, user.key)
      logging.info('Sent reminder to: ' + user.email)

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
      logging.info('Received a message from: ' + mail_message.sender)
      plaintext_bodies = message.bodies('text/plain')
      logging.info('Message: ' + plaintext_bodies)
    
routes = [
  ('/mail/send-reminders', SendReminderEmails),
  ('/_ah/mail/replies@appid.appspotmail.com', LogSenderHandler)
]

app = webapp2.WSGIApplication(routes, debug=settings.DEBUG)