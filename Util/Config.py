#!/usr/bin/env python

import os

from ConfigParser import SafeConfigParser as ConfigParser
from os import path
from sys import argv

import Constants
import Errors

__CONFIG = ConfigParser()

__LOADED = False
try:
    if not path.exists(Constants.CONFIGSTORE):
        os.mkdir(Constant.CONFIGSTORE)
    with open(Constants.CONFIGSTORE, 'r') as conf:
        __CONFIG.readfp(conf)
    __LOADED = True
except:
    pass

def __config_check():
    if not __LOADED:
        raise Errors.ConfigNotFound('Config File Not Found. Execute with ' + 
                    '--generate-config to create configuration file')

def get (section, option, parser=lambda val: val, errors=False):
    __config_check()
    if not __CONFIG.has_section(section):
        raise Errors.ConfigOptionNotFound('Section \'%s\' does not exist' % section)
    if __CONFIG.has_option(section, option):
        return parser(__CONFIG.get(section, option))
    else:
        if errors:
            raise Errors.ConfigOptionNotFound(('Section \'%s\' does not contain' + 
                                    ' option \'%s\'.') % (section, option))
        else:
            return None

def set (section, option, value, persist=False):
    __config_check()
    if not __CONFIG.has_section(section):
        __CONFIG.add_section(section)
    __CONFIG.set(section, option, value)
    if persist:
        with open(Constants.CONFIGSTORE, 'w') as conf:
            __CONFIG.write(conf)

def save():
    with open(Constants.CONFIGSTORE, 'w') as conf:
        __CONFIG.write(conf)

def get_ignores():
    ignore = [u'.GoogleDriveSync/']
    if path.exists(Constants.SYNCIGNORE):
        with open(Constants.SYNCIGNORE, 'r') as igfile:
            for line in igfile:
                line = unicode(line.strip())
                if len(line) and line[0] != u'#':
                    ignore.append(line)
    return ignore
