#!/usr/bin/env python

import re
from GoogleDriveSync import GDrive, Local
from GoogleDriveSync.Auth import get_service
from GoogleDriveSync.Sync import SyncManager

service = get_service()
remote = GDrive.Files(service)
local = Local.Files()

syncer = SyncManager(local, remote)

syncer.sync()
