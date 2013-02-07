Sync algorithm notes
====================

To sync files follow this algorithm:

Load cache of items already synced
Get file system tree
get remote list
for each item in cache sync local and remote and mark nodes processed
for each item in local that is not marked processed sync local and remote, mark processed and update cache
for each item in remote that is not marked processed download and update cache
save updated cache

Sync item follows following rules:

    If item exists in cache:
        if local mtime and length match cache and remote mtime and length match cache do nothing
        if local mtime and length match cache but remote mtime and length do not:
            if remote mtime > local mtime download update
            else raise conflict
        if local mtime and length do not match cache but remote mtime and length do:
            if local mtime > remote mtime upload changes
            else raise conflict
        if neither local nor remote mtime and length match cacheL
            if local mtime and length match remote mtime and length update cache and take no other action
            else if local length and md5 match remote length and md5 update cache and mtimes to most recent 
                mtime and take no other action
            else raise conflict
    else if item is remote item
        if local item exists:
            if local length and md5 match remote length and md5 add item to cache, ensure mtimes are most recent
            else raise conflict
        else if local parent path is not a directory
            try to create directory. if failure raise conflict
            download remote and add to cache
        else parent path is a directory
            download remote and add to cache
    else item is local item
        if remote item exists:
            if local length and md5 match remote length and md5 add item to cache, ensure mtimes are most recent
        else if remote parents is not a folder
            try to create parent folders. if failure raise conflict
            upload new item and add to cache
        else remote parents are folder
            uploade new item and add to cache

    
