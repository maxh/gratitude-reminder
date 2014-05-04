"""drive_manager.py: Helper functions for interfacing with the Drive API."""

import logging

import lib # All third-party libraries are in this module.
import gdata.spreadsheets.client
import gdata.spreadsheet.service
import gdata.client
import gdata.service
import httplib2
from apiclient.discovery import build
from oauth2client.appengine import AppAssertionCredentials

import settings
from secrets import keys


TEMPLATE_ID = '1KW7wgVbojOlDdvbs44trJxz9CCKKgL8P2SPd5l016SU'


def create_authorized_http(scope):
    credentials = AppAssertionCredentials(scope)
    http = httplib2.Http()
    return credentials.authorize(http)


def create_drive_service(http=None):
    """Builds and returns a Drive service object authorized with the
    application's service account.

    Returns:
        Drive service object.
    """
    if http is None:
        http = create_authorized_http(
            scope='https://www.googleapis.com/auth/drive')
    # When running in debug mode on the dev_appserver, service accounts require
    # a few flags to be set. See: http://stackoverflow.com/a/22723127/1691482
    # These flags don't play nice with the api_key.
    if (settings.DEBUG):
      return build('drive', 'v2', http=http)
    return build('drive', 'v2', http=http, developerKey=keys.api_key)


def create_spreadsheet_service():
    """Builds and returns a Spreadsheet service object authorized with the
    application's service account.

    Returns:
        Spreadsheet service object.
    """
    http = create_authorized_http('https://spreadsheets.google.com/feeds')
    create_drive_service(http) # Why is this necessary? Inspired by:
                               # http://stackoverflow.com/a/21468060/1691482
    service = gdata.spreadsheet.service.SpreadsheetsService()
    service.additional_headers = {'Authorization': 'Bearer %s' %
                                  http.request.credentials.access_token}
    return service


def give_user_ownership(service, file_id, user_email):
    """Transfers ownership of the file with file_id to user_email.

    Returns:
        Drive permission object.
    """
    new_permission = {
      'value': user_email,
      'type': 'user',
      'role': 'owner'
    }
    try:
        return service.permissions().insert(
          fileId=file_id, body=new_permission
          #,sendNotificationEmails=False
          ).execute()
    except Exception as e:
        logging.exception(e)
    return None


def create_responses_spreadsheet(user_email):
    """Create a responses spreadsheet in the user's Google Drive.

    Returns:
        ID of the user's new response spreadsheet.
    """
    logging.debug("Now in create_responses_spreadsheet")
    service = create_drive_service()
    body = {'title': 'Gratitude Reminder Responses'}
    copy = service.files().copy(fileId=TEMPLATE_ID, body=body).execute()
    copy_id = copy['id']
    give_user_ownership(service, copy['id'], user_email)
    return copy_id


def add_gratitude_response(file_id, response, date):
    """Appends the response to the spreadsheet indicated by file_id."""
    logging.debug("Now in add_gratitude_response")
    service = create_spreadsheet_service()
    worksheets = service.GetWorksheetsFeed(key=file_id)
    worksheet_id = worksheets.entry[0] # Not doing what I want.
    row_data = {'date': date,
                'response': response}
    logging.info(row_data)
    logging.info(file_id)
    logging.info(worksheet_id)
    logging.info(type(worksheet_id))
    service.InsertRow(row_data=row_data, key='1SIknqNT-YH9gjPQr2Oghp03DzHW3Vmt_uTefoAw-8sM', wksht_id=1)


def generate_web_link(file_id):
    return 'https://docs.google.com/spreadsheets/d/' + file_id
