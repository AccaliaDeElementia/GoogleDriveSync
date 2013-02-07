#!/usr/bin/env python

import os
import re

from os import path
from datetime import datetime
from fnmatch import fnmatch

import Config

class File (object):
    def __getmtime (self):
        # strip sub millisecond info from the timestamp
        # Google drive does not provide resolution greater than millisecond
        time = int(path.getmtime(self.path)*1000)/1000.0
        return datetime.utcfromtimestamp(time)

    def __init__ (self, path_):
        self.path = path_
        self.title = path.basename(path_)
        self.modified = self.__getmtime()
        self.isdir = path.isdir(path_)
        self.processed = False

    def __str__ (self):
        return self.path

class Files (object):
    def __keys (self, item):
        tokens = self.__tokens(item.path)
        return tuple(int(num) if num else alpha.lower() for 
                num, alpha in tokens)

    def __init__ (self):
        self.__ignore = Config.get_ignores()
        self.__tokens = re.compile(r'(\d+)|(\D+)').findall
        self.__load()

    def __load (self):
        self.__items = []
        self.__paths = {}
        for root, dirs, files in os.walk(u'.'):
            if root != u'.':
                item = File(root)
                self.__items.append(item)
                self.__paths[item.path] = item
            i = 0
            while i < len(dirs):
                if self.__filter_file(root, dirs[i], True):
                    i += 1
                else:
                    del dirs[i]
            for item in files:
                if self.__filter_file(root, item):
                    item = File(root + os.sep + item)
                    self.__items.append(item)
                    self.__paths[item.path] = item
        self.__items.sort(key=self.__keys)

    def __iter__(self):
        for item in self.__items:
            yield item

    def __filter_file (self, root, name, isDir=False):
        keep = True
        for pattern in self.__ignore:
            if pattern[-1] == u'/':
                if isDir:
                    pattern = pattern[:-1]
                else:
                    continue
            item = name
            if u'/' in pattern:
                item = root + os.sep + item
            keep = keep and not fnmatch(item, pattern)
            if not keep: 
                break
        return keep
    def get_by_path (self, path):
        return self.__paths.get(path)
