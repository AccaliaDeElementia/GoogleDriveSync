#!/usr/bin/env python

import re
import os
from datetime import datetime

class File (object):
    def __init__ (self, item, path=None):
        self.id = item['id']
        self.path = path
        self.title = item.get('title')
        # TODO: make this parse more robust, just incase google changes it
        self.modified = datetime.strptime(
                            item['modifiedDate'],'%Y-%m-%dT%H:%M:%S.%fZ')
        self.isdir = item['mimeType'] == u'application/vnd.google-apps.folder'
        self.processed = False

    def __str__(self):
        return self.path

class Files(object):
    def __init__ (self, service):
        self.__service = service
        self.__ignored = []
        self.__files = None
        self.__paths = None
        self.__ids = None
        self.__modct = 0
    
    def __iter__(self):
        modct = self.__modct + 1
        self.__refresh()
        for item in self.__files:
            if modct != self.__modct:
                raise Exception('Concurrent modification')
            yield item

    def __fetch(self):
        self.__modct += 1
        files = []
        map_ = {}
        page = None
        while True:
            param = {
                'fields': 'nextPageToken,items(id,title,mimeType,' +
                          'downloadUrl,fileSize,modifiedDate,parents(id),' +
                          'exportLinks,labels,md5Checksum)'
            }
            if page:
                param['pageToken'] = page
            items = self.__service.files().list(**param).execute()
            files.extend(items['items'])
            for item in items['items']:
                map_[item['id']] = item
            page = items.get('nextPageToken')
            if not page:
                break
        return files, map_

    @staticmethod
    def __path(item, map_):
        path_ = [item.get('title')]
        while item:
            pars = []
            for par in item['parents']:
                parent = map_.get(par['id'])
                if parent:
                    pars.append(parent)
            if len(pars) > 1:
                return None
            elif len(pars) == 1:
                path_.insert(0, pars[0]['title'])
            item = pars[0] if pars else None
        return './'+os.sep.join(path_)

    @staticmethod
    def __make_sorted(unsorted, getkey=lambda item: str(item)):
        tokenize = re.compile(r'(\d+)|(\D+)').findall
        key = lambda item2: tuple(int(num) if num else alpha.lower() for 
                num, alpha in tokenize(getkey(item2)))
        return list(sorted(unsorted, key=key))

    def __refresh (self):
        try:
            self.__ignored = []
            files, map_ = self.__fetch()
            items = []
            paths = {}
            ids = {}
            for item in files:
                if item['labels']['trashed']:
                    continue
                path = self.__path(item, map_)
                if path:
                    file = File(item, path)
                    items.append(file)
                    paths[path] = file
                    ids[item['id']] = file
                else:
                    self.__ignored.append(File(item))
            self.__files = self.__make_sorted(items, lambda x: x.path)
            self.__paths = paths
            self.__ids = ids
        except:
            self.__ignored = []
            self.__files = None
            self.__paths = None
            self.__ids = None
            raise
