from datetime import datetime
import logging
import re
import webapp2

# App Engine imports.
from google.appengine.ext import ndb
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

# File imports.
import drive_manager
import mailman
import models
import settings


class SendReminderEmails(webapp2.RequestHandler):

  def get(self):
    users = models.User.query().fetch()
    for user in users:
      mailman.send_reminder(user.email,
                          drive_manager.generate_web_link(user.file_id),
                          'http://www' + settings.URL + '/depart?' + user.email)
      logging.info('Sent reminder to: ' + user.email)


class ReminderReplyHandler(InboundMailHandler):

  def receive(self, mail_message):
    logging.info('Received a message from: ' + mail_message.sender)
    # Sender is formatted like "A B <ab@x.com>"; we need to extract the email.
    sender_email = re.sub(r'.*<(.*@.*\..*)>.*', r'\1', mail_message.sender)
    # There might be multiple message bodies, but we'll only read the first.
    plaintext_body = mail_message.bodies('text/plain').next()[1].decode()
    logging.info(plaintext_body)
    stripping_regex = re.compile('(\n+On .*wrote.*:.*)', re.DOTALL)
    stripped_body = stripping_regex.sub(r'', plaintext_body)
    logging.info('Stripped message:')
    logging.info(stripped_body)
    # The date for this blessing is encoded in the reply to email address on the
    # original message: blessing+YYYY-MM-DD@APP_ID.appspotmail.com.
    # Here we extract the date:
    user = models.User.query(models.User.email == sender_email).fetch(1)[0]
    drive_manager.add_gratitude_response(user.file_id, stripped_body,
                                         datetime.today().strftime('%Y-%m-%d'))


routes = [
  ('/mail/send-reminders', SendReminderEmails),
  ('/_ah/mail/response_handler.*', ReminderReplyHandler)
]


app = webapp2.WSGIApplication(routes, debug=settings.DEBUG)
