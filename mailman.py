from datetime import datetime

# App Engine imports.
from google.appengine.api import mail

# File imports.
import settings


def send_welcome(user_email, responses_url):
  message = mail.EmailMessage()
  message.to = user_email
  message.sender = 'Gratitude Reminder <abbot@%s>' % (settings.URL)
  message.subject = 'Welcome to Gratitude Reminder'
  message.body = '''Namaste,

The deal is:

1. Every day you'll receive an email from me.
2. Reply with something you're grateful for.
3. Visit your <a href="%s">Gratitude Reminder Responses Google Spreadsheet<a> to see your past responses.

You can unsubscribe at anytime.

The Abbot

''' % (responses_url)
  message.send()


def send_reminder(user_email, responses_url, unsubscribe_url):
  message = mail.EmailMessage()
  message.to = user_email
  message.sender = 'Gratitude Reminder <abbot@%s>' % (settings.URL)
  message.subject = 'What are you grateful for today?'
  message.reply_to = 'Gratitude Reminder <blessings@%s.appspotmail.com>' % (
    settings.APP_ID)
  message.html = '''<p>Reply with a few words or sentences.</p>

<p>
<a href="%s">View your previous replies</a> | <a href="%s">Unsubscribe</a>
</p>
''' % (responses_url, unsubscribe_url)
  message.send()
