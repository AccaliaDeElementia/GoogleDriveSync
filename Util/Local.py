#!/usr/bin/env python

import os
import re

from os import path
from fnmatch import fnmatch

import Config

class File (object):
    def __init__ (self, path_):
        self.path = path_
        self.title = path.basename(path_)

    def __str__ (self):
        return self.path

class Files (object):
    def __keys (self, item):
        tokens = self.__tokens(item)
        return tuple(int(num) if num else alpha.lower() for 
                num, alpha in tokens)
    def __init__ (self):
        self.__ignore = Config.get_ignores()
        self.__tokens = re.compile(r'(\d+)|(\D+)').findall

    def __iter__ (self):    
        for root, dirs, files in os.walk(u'.'):
            yield File(root)
            i = 0
            while i < len(dirs):
                if self.__filter_file(root, dirs[i], True):
                    i += 1
                else:
                    del dirs[i]
            dirs.sort(key=self.__keys)
            files.sort(key=self.__keys)
            for item in files:
                if self.__filter_file(root, item):
                    yield File(root + os.sep + item)

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
                
