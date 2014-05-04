

def createDriveService():
  """Builds and returns a Drive service object authorized with the
  application's service account.

  Returns:
    Drive service object.
  """
  credentials = AppAssertionCredentials(
      scope='https://www.googleapis.com/auth/drive')
  http = httplib2.Http()
  http = credentials.authorize(http)
  # When running in debug mode on the dev_appserver, Service Accounts require
  # a few flags to be set.  See: http://stackoverflow.com/a/22723127/1691482
  # These flags don't play nice with the api_key.
  if (settings.DEBUG):
      return build('drive', 'v2', http=http)
  return build('drive', 'v2', http=http, developerKey=keys.api_key)
  service

def add_permission(service, file_id):
    new_permission = {
      'value': 'maxheinritz@gmail.com',
      'type': 'user',
      'role': 'owner'
    }
    try:
        return service.permissions().insert(
            fileId=file_id, body=new_permission).execute()
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    return None

def create_responses_spreadsheet(credentials):
    """Create a responses spreadsheet in the user's Google Drive.
    """
    # Create an httplib2.Http object and authorize it with our credentials
    service = createDriveService()
    logging.info(service.about().get().execute())
    body = {'title': 'Gratitude Reminder Responses from template test'}
    #    copy = service.files().copy(fileId='1KW7wgVbojOlDdvbs44trJxz9CCKKgL8P2SPd5l016SU',
    #                                body=body).execute()
    #    logging.info(copy)
    logging.info(add_permission(service, '10Rq_q3axlCSZed93k4Rlk9_kkDTde6e6kK5p4vSJYBs'))
    '''http = httplib2.Http()
    http = credentials.authorize(http)
    drive_service = build('drive', 'v2', http=http)
    # Insert a file
    mime_type = 'application/vnd.google-apps.spreadsheet'
    media_body = MediaFileUpload('data/responses_template.gsheet', mimetype=mime_type, resumable=True)
    body = {
        'title': 'Gratitude Reminder Responses from template',
        'mimeType': mime_type,
    }
    spreadsheet = drive_service.files().insert(body=body,
                                               media_body=media_body,
                                               convert=True,
                                               visibility='PRIVATE').execute()

    spreadsheet = drive_service.files().get(fileId='https://www.googleapis.com/drive/v2/files/1KW7wgVbojOlDdvbs44trJxz9CCKKgL8P2SPd5l016SU').execute()
    logging.info(spreadsheet)'''
    # Because formatting isn't supported via the Google Spreadsheets API, we'll need
    # create a copy of a pre-formatted responses template spreadsheet using the Drive
    # API.
    # https://developers.google.com/drive/v2/reference/files/copy
    # We'll still need to use the Spreadsheets API for inserting new rows, so all this other
    # work was not lost.
    # Initialize the spreadsheet.
    '''headers = {}
    credentials.apply(headers) # Set the authentication header using OAuth Token
    service = gdata.spreadsheet.service.SpreadsheetsService(additional_headers=headers)
    worksheets = service.GetWorksheetsFeed(key=spreadsheet['id'])
    # Set the size of spreadsheet's default worksheet to 2 columns by 10 rows.
    worksheet = worksheets.entry[0]
    worksheet.row_count = gdata.spreadsheet.RowCount(text=str(10))
    worksheet.col_count = gdata.spreadsheet.ColCount(text=str(10))
    service.UpdateWorksheet(worksheet)
    logging.info(worksheet)'''
