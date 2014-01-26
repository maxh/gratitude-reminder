from datetime import datetime

# App Engine imports.
from google.appengine.api import mail

# File imports.
import settings


def sendVerification(user_email, verification_key):
  message = mail.EmailMessage()
  message.to = user_email
  message.sender = 'Gratitude Reminder <abbot@%s>' % (settings.URL)
  message.subject = 'Gratitude Reminder Verfication'
  # Does it matter that the URL includes the user's unobfuscated email address?
  message.body = '''Namaste,

Please click the link below to confirm that you\'d like to be reminded to be grateful:

http://www.%s/verify?e=%s&k=%s

The deal is:

1. Every day you'll receive an email from me.
2. Reply with something you're grateful for.
3. Return to www.%s to see your past responses.

You can unsubscribe at anytime.

The Abbot

''' % (settings.URL, user_email, verification_key, settings.URL)
  message.send()

def sendReminder(user_email, verification_key):
  message = mail.EmailMessage()
  message.to = user_email
  message.sender = 'Gratitude Reminder <abbot@%s>' % (settings.URL)
  message.subject = 'Gratitude Reminder'
  # Does it matter that the URL includes the user's unobfuscated email address?
  date_string = datetime.today().strftime('%Y-%m-%d')
  message.sender = 'Gratitude Reminder <blessings+%s@%s.appspotmail.com>' % (date_string, settings.APP_ID)
  message.body = '''Namaste,

Reply to this email with a few words describing something you're grateful for.  It can be helpful to be specific.  I often reflect on the previous day to generate ideas.

Your past responses: http://www.%s/history?e=%s&k=%s
Unsubscribe: http://www.%s/depart?e=%s&k=%s

The Abbot

''' % (settings.URL, user_email, verification_key, settings.URL, user_email, verification_key)
  message.send()