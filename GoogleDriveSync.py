import os
import re
import cPickle as pickle

from fnmatch import fnmatch
from os import path
from sys import argv
from ConfigParser import SafeConfigParser as ConfigParser

from httplib2 import Http
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow

class GoogleDriveSyncError(Exception):
    pass

class Config (object): 
    DIR = u'.GoogleDriveSync'
    CONFIG = DIR + os.sep + u'GoogleDriveSync.cfg'
    CREDENTIALS = DIR + os.sep + u'credentials.pkl'
    IGNORE = DIR + os.sep + 'syncignore'
    CACHE = DIR + os.sep + u'GoogleDriveSync.cache'

    __cfg = ConfigParser()
    __loaded = False
    def __load(self):
        if self.__loaded: return
        try:
            if not path.exists(self.DIR):
                os.mkdir(self.DIR)
            with open(self.CONFIG, 'r') as conf:
                self.__cfg.readfp(conf)
            self.__loaded = True
        except Exception, e:
            print e
    def get (self, section, option, parser = unicode, error=False):
        self.__load()
        if not self.__cfg.has_section(section):
            if error:
                raise GoogleDriveSyncError('Section not exist')
            else:
                return None
        if self.__cfg.has_option(section, option):
            return parser(Config.__cfg.get(section, option))
        elif error:
            raise GoogleDriveSyncError('Option not exist')
        return None
    def set(self, section, option, value, persist=False):
        self.__load()
        if not self.__cfg.has_section(section):
            self.__cfg.add_section(section)
        self.__cfg.set(section, option, value)
        if persist:
            with open(self.CONFIG, 'w') as conf:
                self.__cfg.write(cfg)
    def ignore_list(self):
        ignore = [self.DIR+u'/']
        if path.exists(Config.IGNORE):
            with open(Config.IGNORE, 'r') as igfile:
                for line in igfile:
                    line = unicode(line.strip())
                    if len(line) and line[0] != u'#':
                        ignore.append(line)
        return ignore
Config = Config()


class Auth (object):
    def __init__(self):
        self.http = Http()
        self.credentials = None

    def authorize (self):
        if not path.exists(Config.CREDENTIALS):
            raise GoogleDriveSyncError('No stored credentials found. Must authorize first')
        with open(Config.CREDENTIALS, 'rb') as cred:
            self.credentials = pickle.load(cred)
        self.credentials.refresh(self.http)
        self.credentials.authorize(self.http)
        with open(Config.CREDENTIALS, 'wb') as cred:
            pickle.dump(self.credentials, cred, -1)

TOKENIZE = re.compile(r'(\d+)|(\D+)').findall
def get_key(extractor=lambda x: x):
    def key(item):
        return tuple(int(num) if num else alpha.lower() for num, alpha in TOKENIZE(extractor(item)))
    return key

IGNORES = Config.ignore_list()
def fnfilter(path, is_dir=False):
    for pattern in IGNORES:
        if pattern[-1] == u'/':
            if is_dir:
                pattern = pattern[:-1]
            else:
                continue
            if not fnmatch(path, pattern):
                return False
    return True

class GDrive(object):
    class File (object):
        def __init__(self, item):
            self.item = item
            self.path = None
            for name in item.keys():
                setattr(self, name, item[name])
        def __unicode__(self):
            return self.path + os.sep + self.title
        def __str__(self):
            return unicode(self)

    def __init__ (self):
        self.__auth = Auth()
        self.__auth.authorize()
        self.service = build('drive', 'v2', http=self.__auth.http)
    
    def update(self):
        def pather(item, ids):
            path_ = []
            while item:
                pars = []
                for par in item.parents:
                    parent = ids.get(par['id'])
                    if parent:
                        pars.append(parent)
                if len(pars) > 1:
                    return None
                elif len(pars) == 1:
                    path_.insert(0, pars[0].title)
                item = pars[0] if pars else None
            if not path_:
                return u'.'
            return u'.'+os.sep+unicode(os.sep).join(path_)
        paths = {}
        ids = {}
        files = []
        fn = self.service.files().list
        fields = ('nextPageToken,items(id,title,mimeType,downloadUrl,' + 
                 'fileSize,modifiedDate,parents(id),labels,md5Checksum)')
        page = None
        while True:
            params = {'fields': fields}
            if page:
                params['pageToken'] = page
            items = fn(**params).execute()
            for item in items['items']:
                f = self.File(item)
                ids[f.id] = f
            page = items.get('nextPageToken')
            if not page:
                break
        for item in ids.values():
            path = pather(item, ids)
            if path == None: 
                continue
            if item.labels['trashed']:
                continue
            item.path = path
            files.append(item)
            paths[unicode(item)] = item
        files.sort(key=get_key(unicode))
        self.__files = files
        self.__ids = ids
        self.__paths = paths

    def list(self):
        return self.__files

class Local(object):
    class File(object):
        def __init__(self, path):
            self.path = unicode(path)
        def __str__(self):
            return self.path
        def __unicode__(self):
            return self.path

    def __init__(self):
        self.__files = None
        self.__paths = None

    def update(self):
        items = []
        paths = {}
        for root, dirs, files in os.walk(u'.'):
            if root != u'.':
                f = self.File(root)
                items.append(f)
                paths[root] = f
            i = 0
            while i < len(dirs):
                if fnfilter(root+u'/'+dirs[i], True):
                    i += 1
                else:
                    del dirs[i]
            key = get_key()
            dirs.sort(key=key)
            files.sort(key=key)
            for item in files:
                path = root+os.sep+item
                if fnfilter(path):
                    f = self.File(path)
                    items.append(f)
                    paths[path] = f
        self.__files = items
        self.__paths = paths

    def list(self):
        return self.__files

drive = GDrive()
drive.update()
local = Local()
local.update()
print(len(drive.list()))
print(len(local.list()))
for item in local.list():
    print(item.__str__())

#This app has super Fluttershy powers
