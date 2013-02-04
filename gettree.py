#!/usr/bin/python
import pprint
import re
from Util.Auth import get_service

from apiclient import errors

drive_service = get_service()
sort_tokenize = re.compile(r'(\d+)|(\D+)').findall

def sort_strings(input):
    sortkey = lambda x: tuple(int(num) if num else alpha.lower() for num, alpha in sort_tokenize(x))
    return list(sorted(input, key=sortkey))

def get_all_files():
    result = []
    page_token = None
    while True:
        try:
            param = {
                'fields': 'nextPageToken,items(id,title,mimeType,downloadUrl,fileSize,originalFilename,modifiedDate,parents(id),exportLinks,labels)'
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

def get_item_name(item):
    name = item.get('originalFilename')
    if name: return name
    name = item.get('title')
    if name: return name
    raise Exception('Couldn\'t find filename for: %r' % item)

map = get_remote_map()
files = []
for file in map.values():
    parents = get_parents(file, map)
    if len(parents) > 1:
        print 'Ignoring %s because of multiple parents: %r' % (get_item_name(file),parents)
        continue
    path = []
    path.insert(0, get_item_name(file))
    while len(parents) == 1:
        file = parents[0]
        path.insert(0, get_item_name(file))
        parents = get_parents(file, map)
    files.append('/'.join(path))
for f in sort_strings(files):
    print f

