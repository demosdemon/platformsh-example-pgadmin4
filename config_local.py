# -*- coding: utf-8 -*-

import base64
import json
import os

WELL_KNOWN_BASE64_JSON = (
    "PLATFORM_APPLICATION",
    "PLATFORM_VARIABLES",
    "PLATFORM_RELATIONSHIPS",
    "PLATFORM_ROUTES",
)


def env(var_name, default=None, decode=None):
    """
    Grab the `var_name` from the environment if it exists.

    If it does not exist, return `default`.

    If `decode` is None, check `var_name` for `WELL_KNOWN_BASE64_JSON` and decode
    if necessary. If `decode` is True, decode without checking. If `decode` is
    False, do not decode.
    """
    if decode is None:
        decode = var_name in WELL_KNOWN_BASE64_JSON

    try:
        value = os.environ[var_name]
    except KeyError:
        return default

    if decode:
        value = json.loads(base64.b64decode(value.encode("ascii")))

    return value


platform_app_dir = env("PLATFORM_APP_DIR")
platform_application = env("PLATFORM_APPLICATION")
platform_application_name = env("PLATFORM_APPLICATION_NAME")
platform_project = env("PLATFORM_PROJECT")
platform_relationships = env("PLATFORM_RELATIONSHIPS")
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
        raise RuntimeError("{!r} must be created prior to initializing the application.".format(DATA_DIR))

if platform_smtp_host:
    MAIL_SERVER = platform_smtp_host
