#!/usr/bin/env python

class GoogleDriveSyncError (Exception):
    """
    Base error raised by GoogleDriveSync.
    """
    pass

class ConfigError(GoogleDriveSyncError):
    pass

class ConfigNotFound(ConfigError):
    pass

class ConfigOptionNotFound(ConfigError):
    pass
