#!/usr/bin/python

from ConfigParser import ConfigParser
from os import path
import pickle
import httplib2

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow

import Constants
import Config
CLIENT_ID = Config.get('CLIENT', 'ID')
CLIENT_SECRET = Config.get('CLIENT', 'SECRET')
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


def __new_credentials():
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    return credentials

def get_credentials(): 
    if path.exists(Constants.CREDENTIALS):
        with open(Constants.CREDENTIALS, 'rb') as fp:
            return pickle.load(fp)
    else:
        credentials = __new_credentials()
        with open(CREDENTIALS, 'wb') as fp:
            pickle.dump(credentials, fp)
        credentials.refreshToken()
        return credentials

def get_service():
    creds = get_credentials()
    http = httplib2.Http()
    creds.authorize(http)
    service = build('drive', 'v2', http=http)
    return service
