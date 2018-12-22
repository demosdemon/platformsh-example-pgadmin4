# -*- coding: utf-8 -*-

import logging
import os

from psh import env

platform_app_dir = env("PLATFORM_APP_DIR")
platform_application = env("PLATFORM_APPLICATION")
platform_project = env("PLATFORM_PROJECT")
platform_smtp_host = env("PLATFORM_SMTP_HOST")


# Only set pgAdmin4 settings if we are within a Platform.sh environment
if platform_project:
    # Default pgadmin4 settings write to /var/lib/pgadmin which is not writable
    # in psh containers

    # raises KeyError if not found
    mounts = platform_application["mounts"]
    # raises StopIteration if not found
    mount = next(iter(mounts)).lstrip("/")
    DATA_DIR = os.path.join(platform_app_dir, mount)
    LOG_FILE = os.path.join(DATA_DIR, "pgadmin4.log")
    SQLITE_PATH = os.path.join(DATA_DIR, "pgadmin4.db")
    SESSION_DB_PATH = os.path.join(DATA_DIR, "sessions")
    STORAGE_DIR = os.path.join(DATA_DIR, "storage")
    TEST_SQLITE_PATH = os.path.join(DATA_DIR, "test_pgadmin4.db")

    if not os.path.exists(DATA_DIR):
        raise RuntimeError(
            "{!r} must be created prior to initializing the application.".format(
                DATA_DIR
            )
        )

if platform_smtp_host:
    MAIL_SERVER = platform_smtp_host

CONSOLE_LOG_LEVEL = logging.WARNING
FILE_LOG_LEVEL = logging.DEBUG

# Disable version checking
UPGRADE_CHECK_ENABLED = True

# Disable ssh tunneling
SUPPORT_SSH_TUNNEL = False
