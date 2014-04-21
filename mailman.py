from datetime import datetime

# App Engine imports.
from google.appengine.api import mail

# File imports.
import settings


def send_welcome(user_email):
  message = mail.EmailMessage()
  message.to = user_email
  message.sender = 'Gratitude Reminder <abbot@%s>' % (settings.URL)
  message.subject = 'Welcome to Gratitude Reminder'
  # Does it matter that the URL includes the user's unobfuscated email address?
  message.body = '''Namaste,

The deal is:

1. Every day you'll receive an email from me.
2. Reply with something you're grateful for.
3. Return to www.%s to see your past responses.

You can unsubscribe at anytime.

The Abbot

''' % (settings.URL)
  message.send()

def send_reminder(user_email, verification_key):
  message = mail.EmailMessage()
  message.to = user_email
  message.sender = 'Gratitude Reminder <abbot@%s>' % (settings.URL)
  message.subject = 'What are you grateful for today?'
  # Does it matter that the URL includes the user's unobfuscated email address?
  date_string = datetime.today().strftime('%Y-%m-%d')
  message.reply_to = 'Gratitude Reminder <blessings+%s@%s.appspotmail.com>' % (date_string, settings.APP_ID)
  message.html = '''<p>Reply with a few words or sentences.</p>

<p><a href="http://www.%s/blessings?e=%s&k=%s">View your previous replies</a> | 
<a href="http://www.%s/depart?e=%s&k=%s">Unsubscribe</a></p>
''' % (settings.URL, user_email, verification_key, settings.URL, user_email, verification_key)
  message.send()
