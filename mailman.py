# App Engine imports.
from google.appengine.api import mail

# File imports.
import settings

def sendVerificationEmail(user_email, verification_key):
  message = mail.EmailMessage()
  message.to = user_email
  message.sender = 'Gratitude Reminder <abbot@%s>' % (settings.URL)
  message.subject = 'Gratitude Reminder Verfication'
  message.body = '''Namaste,

Please click the link below to confirm that you\'d like to be reminded to be grateful:

http://www.%s/verify?key=%s

The deal is:

1. Every day you'll receive an email from me.
2. Reply with something you're grateful for.
3. Return to www.%s to see your past responses.

You can unsubscribe at anytime.

The Abbot

''' % (settings.URL, verification_key, settings.URL)
  message.send()