#!/usr/bin/env python

import os
from datetime import datetime
from os import path
from magic import Magic
from hashlib import md5
MIME = Magic(mime=True)

def make_hash(name, blocksize=65536):
    with open(name, 'r') as item:
        hash = md5()
        buf = item.read(blocksize)
        while len(buf) > 0:
            hash.update(buf)
            buf = item.read(blocksize)
        return hash.hexdigest()

files = []
for dirpath, dirnames, filenames in os.walk('.'):
    files.append(dirpath)
    for i in xrange(len(dirnames)-1, -1, -1):
        if len(dirnames[i]) < 1: 
            continue
        if dirnames[i][0] == '.':
            del dirnames[i]
    for i in xrange(len(filenames)-1, -1, -1):
        if filenames[i][0] == '.':
            del filenames[i]
    for name in filenames:
        files.append(path.join(dirpath, name))

for file in files:
    mime = MIME.from_file(file)
    omtime = int(path.getmtime(file)*1000)/1000.0
    mtime = datetime.utcfromtimestamp(omtime).strftime('%H-%m-%dT%H:%M:%S.%fZ')
    md5sum = ''
    if mime != 'inode/directory':
        md5sum = make_hash(file)
    print(file, mime, mtime, md5sum)
