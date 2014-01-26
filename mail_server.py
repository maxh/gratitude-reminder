from datetime import datetime
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
    # Sender is formatted like "A B <ab@x.com>"; we need to extract the email.
    sender_email = re.sub(r'.*<(.*@.*\..*)>.*', r'\1', mail_message.sender)
    
    # There might be multiple message bodies, but we'll only read the first.
    plaintext_body = message.bodies('text/plain').next()
    logging.info('Message: ' + plaintext_body)

    # The date for this blessing is encoded in the reply to email address on the
    # original message: blessing+YYYY-MM-DD@APP_ID.appspotmail.com.
    # Here we extract the date:
    date_string = re.sub(r'.*<.*\+(.*-.*-.*)@.*\..*>.*', r'\1', mail_message.to)
    
    user = models.User.query(models.User.email == sender_email).fetch(1)[0]
    blessing = models.Blessing(parent=ndb.Key(models.User, user),
                               content=plaintext_bodies.next(),
                               date=datetime.strptime(date_string,'%Y-%m-%d'))
    blessing.put()

    
routes = [
  ('/mail/send-reminders', SendReminderEmails),
  ('/_ah/mail/replies@appid.appspotmail.com', LogSenderHandler)
]

app = webapp2.WSGIApplication(routes, debug=settings.DEBUG)