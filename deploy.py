#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import os

from config import DATA_DIR, SQLITE_PATH
from pgadmin import create_app
from pgadmin.model import SCHEMA_VERSION, Server, ServerGroup, User, Version, db
from pgadmin.setup import db_upgrade
from psh import env


def mkpassfile(password):
    key = hashlib.sha256(password.encode("utf-8")).hexdigest()
    passfile = os.path.join(DATA_DIR, "{}.pass".format(key))
    with open(passfile, "w") as fp:
        fp.write(password)

    return passfile


def setup_db():
    app = create_app()

    with app.app_context():
        if not os.path.exists(SQLITE_PATH):
            print("Initializing database for the first time.")
            db_upgrade(app)
        else:
            version = Version.query.filter_by(name="ConfigDB").first()
            if version is None:
                print(
                    "Error fetching database version. Removing database and reinitializing."
                )
                os.unlink(SQLITE_PATH)
                db_upgrade(app)
            else:
                schema_version = version.value

                if SCHEMA_VERSION >= schema_version:
                    print("Upgrading database schema.")
                    db_upgrade(app)

                if SCHEMA_VERSION > schema_version:
                    version = Version.query.filter_by(name="ConfigDB").first()
                    version.value = SCHEMA_VERSION
                    print("Saving database schema version.")
                    db.session.commit()


def get_relationships():
    relationships = env("PLATFORM_RELATIONSHIPS")
    for group, nodes in relationships.items():
        for node in nodes:
            if node["scheme"] == "pgsql":
                yield {
                    "name": node["cluster"],
                    "host": node["host"],
                    "group": group,
                    "port": node["port"],
                    "username": node["username"],
                    "passfile": node["password"],
                    "ssl_mode": "prefer",
                    "maintenance_db": "postgres",
                }


def get_or_create_group_id(name, user_id):
    group = ServerGroup.query.filter_by(user_id=user_id, name=name).first()
    if group is None:
        group = ServerGroup()
        group.name = name
        group.user_id = user_id
        print("Created server group %s for user id %d" % (name, user_id))
        db.session.add(group)

        try:
            db.session.commit()
        except Exception:
            raise RuntimeError("Error creating server group %s" % (name,))
        else:
            print("Successfully saved.")

    return group.id


def add_relationships():
    app = create_app()

    with app.app_context():
        email = env("PGADMIN_SETUP_EMAIL")
        if not email:
            raise RuntimeError("Expected $PGADMIN_SETUP_EMAIL environment variable.")

        user = User.query.filter_by(email=email).first()
        if user is None:
            raise RuntimeError(
                "The specified user ID ({}) could not be found.".format(email)
            )
        user_id = user.id

        rels = list(get_relationships())

        for rel in rels:
            group = rel.pop("group")
            name = rel.pop("name")
            group_id = get_or_create_group_id(group, user_id)

            server = Server.query.filter_by(group_id=group_id, name=name).first()
            if server is None:
                server = Server()
                server.name = name
                server.group_id = group_id
                server.user_id = user_id
                print(
                    "Created server %s in group %s for user id %d"
                    % (name, group, user_id)
                )
                db.session.add(server)

            for key, value in rel.items():
                setattr(server, key, value)

            try:
                db.session.commit()
            except Exception:
                raise RuntimeError("Error saving server %s - %s" % (group, name))
            else:
                print(
                    "Successfully saved server %s in group %s for user id %d"
                    % (name, group, user_id)
                )


if __name__ == "__main__":
    setup_db()
    add_relationships()
