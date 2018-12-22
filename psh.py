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
    if necessary. If `decode` is True, decode without checking. If `decode`
    is False, do not decode.
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
