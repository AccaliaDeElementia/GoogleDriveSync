#!/usr/bin/env python

import cPickle as pickle

from os import path

import Constants

class SyncInfo (object):
    def __init__ (self, id, path, modified):
        self.id = id
        self.path = path
        self.modified = modified

class SyncMap (object):
    def __init__ (self):
        self.__ids = {}
        self.__paths = {}

    def register (self, syncinfo):
        self.__ids[syncinfo.id] = syncinfo
        self.__paths[syncinfo.path] = syncinfo

    def get_by_id (self, id):
        return self.__ids.get(id)

    def get_by_path (self, path):
        return self.__paths.get(path)

    def save(self):
        with open(Constants.SYNCINFO, 'wb') as syncinfo:
            pickle.dump(self, syncinfo, -1)

    @staticmethod
    def load():
        try:
            with open(Constants.SYNCINFO, 'rb') as syncinfo:
                return pickle.load(syncinfo)
        except Exception,e:
            print 'oops. no map to load or something'
            print str(e)
        return SyncMap()

class SyncManager (object):
    def __init__(self, local, remote, service):
        self.__local = local
        self.__remote = remote
        self.__service = service
        self.__map = SyncMap.load()

    def sync(self):
        for remote in self.__remote:
            status = ''
            m = self.__map.get_by_id(remote.id)
            if not m:
                status += 'newremote '
                if path.exists(remote.path):
                    local = self.__local.get_by_path(remote.path)
                    local.processed = True
                    status += 'conflict '
            else:
                status += 'resync '
                if not path.exists(m.path):
                    status += 'deleted '
                else:
                    local = self.__local.get_by_path(m.path)
                    local.processed = True
                    if local.modified == m.modified and m.modified != remote.modified:
                        status = 'download '
                    elif local.modified != m.modified and m.modified == remote.modified:
                        status = 'upload '
                    elif local.modified != remote.modified:
                        status = 'conflict'
            print (status, remote.path)
        for local in self.__local:
            if local.processed:
                continue
            print ('newlocal', local.path)

    def resolveConflict (self, local, remote):
        print u'conflict for: %s (%s)' % (local, remote)
