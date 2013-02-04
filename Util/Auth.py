#!/usr/bin/python

from ConfigParser import ConfigParser
from os import path
import pickle
import httplib2

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow


# Copy your credentials from the APIs Console
CONFIGDIR = '.GoogleDriveSync'
CONFIGSTORE = path.join(CONFIGDIR, 'config.cfg')
CREDENTIALS = path.join(CONFIGDIR, 'credentials')

CONFIG = ConfigParser()
with open(CONFIGSTORE, 'r') as fp:
    CONFIG.readfp(fp)
CLIENT_ID = CONFIG.get('CLIENT', 'ID')
CLIENT_SECRET = CONFIG.get('CLIENT', 'SECRET')
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
    if path.exists(CREDENTIALS):
        with open(CREDENTIALS, 'rb') as fp:
            return pickle.load(fp)
    else:
        credentials = __new_credentials()
        with open(CREDENTIALS, 'wb') as fp:
            pickle.dump(credentials, fp)
        return credentials

def get_service():
    creds = get_credentials()
    http = httplib2.Http()
    creds.authorize(http)
    service = build('drive', 'v2', http=http)
    return service
