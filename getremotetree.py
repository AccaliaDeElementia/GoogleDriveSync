#!/usr/bin/python
import pprint
import re
from Util.Auth import get_service

from apiclient import errors

drive_service = get_service()
sort_tokenize = re.compile(r'(\d+)|(\D+)').findall

def sort_strings(input, getkey=lambda x:x):
    sortkey = lambda x: tuple(int(num) if num else alpha.lower() for num, alpha in sort_tokenize(getkey(x)))
    return list(sorted(input, key=sortkey))

def get_all_files():
    result = []
    page_token = None
    while True:
        try:
            param = {
                'fields': 'nextPageToken,items(id,title,mimeType,downloadUrl,fileSize,originalFilename,modifiedDate,parents(id),exportLinks,labels,md5Checksum)'
            }
            if page_token:
                param['pageToken'] = page_token
            files = drive_service.files().list(**param).execute()
            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError, error:
            print 'ERROR: %s' % error
        return result

def get_remote_map():
    files = get_all_files()
    map = {}
    for file in files:
        map[file['id']] = file
    return map

def get_parents(item, map):
    parents = []
    for par in item['parents']:
        parent = map.get(par['id'])
        if parent:
            parents.append(parent)
    return parents

map = get_remote_map()
files = []
for file in map.values():
    name = file.get('title')
    parents = get_parents(file, map)
    if len(parents) > 1:
        print 'Ignoring "%s" because it has multiple parents: %r' % (name,parents)
        continue
    if file['labels']['trashed']:
        print 'Ignoring "%s" because it is Trashed.' % name
    path = []
    path.insert(0, name)
    mimetype = file['mimeType']
    modDate = file['modifiedDate']
    size = file.get('fileSize','')
    checksum = file.get('md5Checksum', '')
    links = file.get('exportLinks')
    if not links: 
        links = {}
    links[mimetype] = file.get('downloadUrl')
    while len(parents) == 1:
        file = parents[0]
        path.insert(0, file.get('title'))
        parents = get_parents(file, map)
    files.append(('./' + '/'.join(path),mimetype,modDate,size,checksum, links))
for f in sort_strings(files, lambda x: x[0]):
    print f

