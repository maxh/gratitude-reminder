Gratitude Reminder
==================

[gratitudereminder.org](http://www.gratitudereminder.org/)

### How to get your local dev_appserver.py working

1.  Install the [Google App Engine SDK for Python](https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python).
2. Create a `secrets/keys.py` file that defines [your project's API key](https://developers.google.com/api-client-library/python/guide/aaa_apikeys) as `api_key`.
3. [Create and configure a service account for your project](http:/stackoverflow.com/a/22723127/1691482).
4. Start the local test server using the Google App Engine SDK for Python.
Your command may look something like:

    dev_appserver.py --log_level debug --appidentity_email_address \
    <some-id>@developer.gserviceaccount.com --appidentity_private_key_path \
    secrets/private_key_for_dev_appserver.pem --clear_datastore=yes ./
