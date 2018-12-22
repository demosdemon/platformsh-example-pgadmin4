# -*- coding: utf-8 -*-

import logging
import os

from psh import env

#: Control the verbosity of the log messages in `LOG_FILE`
FILE_LOG_LEVEL = logging.DEBUG

#: Control the verbosity of the log messages in `/var/log/app.log`
CONSOLE_LOG_LEVEL = logging.WARNING

#: Disable checking for updates, unecessary http call for every request
UPGRADE_CHECK_ENABLED = True

#: Optionally disable ssh tunneling via environment variables. SSH tunneling
#: is not necessary to connect to platform.sh databases within the same cluster,
#: however SSH tunneling may be used to connect to database instances in other
#: clusters via the application host
SUPPORT_SSH_TUNNEL = env("PGADMIN4_SUPPORT_SSH_TUNNEL", "false").lower() == "true"


def platform_settings():
    platform_app_dir = env("PLATFORM_APP_DIR")
    platform_application = env("PLATFORM_APPLICATION")
    platform_project = env("PLATFORM_PROJECT")
    platform_smtp_host = env("PLATFORM_SMTP_HOST")

    # Only set pgAdmin4 settings if we are within a Platform.sh environment.
    if not platform_project:
        return

    # raises: KeyError if no mounts are defined
    # raises: TypeError if PLATFORM_APPLICATION was not found
    mounts = platform_application["mounts"]

    # raises: StopIteration if no mounts are defined
    # selects the first mount from the `.platform.app.yaml`
    # strip off leading "/" so we can use `os.path.join`
    mount = next(iter(mounts)).lstrip("/")

    # By default, pgAdmin4 tries to write to `/var/lib/pgadmin` which is RO
    # in a psh container. We need to override the default setting with our
    # writable mount
    data_dir = os.path.join(platform_app_dir, mount)

    # log_file is where pgAdmin4 output informational messages in addition
    # to the console messages.
    log_file = os.path.join(data_dir, "pgadmin4.log")

    # sqlite_path is where pgAdmin4 stores user and server information
    sqlite_path = os.path.join(data_dir, "pgadmin4.db")

    # session_db_path is where pgAdmin4 stores temporary session data
    session_db_path = os.path.join(data_dir, "sessions")

    # storage_dir is where pgAdmin4 stores intermeidate storage for queries
    storage_dir = os.path.join(data_dir, "storage")

    # test_sqlite_path is where pgAdmin4 stores its test database when running
    # unit tests. It's not necessary to test this value, but we're being
    # explicit.
    test_sqlite_path = os.path.join(data_dir, "test_pgadmin4.db")

    # assert that the data_dir was created during build, it is most likely too
    # late for use to create it now
    if not os.path.exists(data_dir):
        raise FileNotFoundError(
            "Expected {!r} to be created prior to initializing the application.".format(
                data_dir
            )
        )

    # directly modify the globals dict and add our updated settings to prevent
    # poluting the `config` namespace with unecessary variables
    globals().update(
        DATA_DIR=data_dir,
        LOG_FILE=log_file,
        SQLITE_PATH=sqlite_path,
        SESSION_DB_PATH=session_db_path,
        STORAGE_DIR=storage_dir,
        TEST_SQLITE_PATH=test_sqlite_path,
        MAIL_SERVER=platform_smtp_host,
    )


platform_settings()
del platform_settings
