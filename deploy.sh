#!/bin/sh

fatal() {
  printf 'E: %s\n' "$@" >&2;
  exit 1
}

if [ -z "${PGADMIN_PATH}" ]; then
  fatal 'You must define the PGADMIN_PATH environment variable.'
fi

if [ -z "${PGADMIN_DATA}" ]; then
  fatal 'You must define the PGADMIN_DATA environment variable.'
fi

if [ ! -f "${PGADMIN_DATA}/pgadmin4.db" ]; then
  if [ -z "${PGADMIN_DEFAULT_EMAIL}" -o -z "${PGADMIN_DEFAULT_PASSWORD}" ]; then
    fatal 'You must define the PGADMIN_DEFAULT_EMAIL and PGADMIN_DEFAULT_PASSWORD environment variables.'
  fi

  export PGADMIN_SETUP_EMAIL=${PGADMIN_DEFAULT_EMAIL}
  export PGADMIN_SETUP_PASSWORD=${PGADMIN_DEFAULT_PASSWORD}

  python "${PGADMIN_PATH}/setup.py"
fi
