#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from config import SQLITE_PATH
from pgadmin import create_app
from pgadmin.model import SCHEMA_VERSION, Server, ServerGroup, User, Version, db
from pgadmin.setup import db_upgrade
from pgadmin.utils.crypto import encrypt
from psh import env

DISCOVERY_ID = "platformsh"


def commit(errmsg=None, success=None):
    try:
        db.session.commit()
    except Exception as e:
        raise RuntimeError(errmsg if errmsg else str(e))
    else:
        if success:
            print(success)


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
                    commit("Error saving database schema version")


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
                    "password": node["password"],
                    "passfile": None,
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

        commit("Error creating server group {}".format(name), "Successfully saved.")

    return group.id


def create_or_update_server(user, server_dict):
    group = server_dict.pop("group")
    name = server_dict.pop("name")
    password = server_dict.pop("password")
    group_id = get_or_create_group_id(group, user.id)

    server = Server.query.filter_by(
        user_id=user.id, servergroup_id=group_id, name=name
    ).first()
    if server is None:
        server = Server(name=name, servergroup_id=group_id, user_id=user.id)
        print(
            "Created server {!r} in group {!r} for user {!r}".format(
                name, group, user.email
            )
        )
        db.session.add(server)

    server.password = encrypt(password, user.password)
    server.discovery_id = DISCOVERY_ID

    for attr, value in server_dict.items():
        setattr(server, attr, value)

    commit(
        "Error updating server {} in group {}".format(name, group),
        "Successfully saved.",
    )
    return server


def prune_old_servers(user, discovered):
    existing = Server.query.filter_by(user_id=user.id, discovery_id=DISCOVERY_ID).all()
    pruned_servers = []
    pruned_groups = []
    for server in existing:
        if server in discovered:
            continue

        group = ServerGroup.query.filter_by(id=server.servergroup_id).first()
        print(
            "Removing {!r} from {!r} as it was not in the environment.".format(
                server.name, group.name
            )
        )

        db.session.delete(server)
        commit("Error removing server.", "Successfully saved.")
        pruned_servers.append(server)

        servers = Server.query.filter_by(servergroup_id=group.id).count()
        if servers == 0 and group.name != "Servers":  # Servers is a protected group
            print("Removing group {!r} because it is empty.".format(group.name))
            db.session.delete(group)
            commit("Error removing group.", "Successfully saved.")
            pruned_groups.append(group)

    return pruned_servers, pruned_groups


def add_relationships():
    app = create_app()

    with app.app_context():
        email = env("PGADMIN_SETUP_EMAIL")
        if not email:
            raise RuntimeError("Expected $PGADMIN_SETUP_EMAIL environment variable.")

        user = User.query.filter_by(email=email).first()
        if user is None:
            raise RuntimeError(
                "The specified user {!r} could not be found.".format(email)
            )

        rels = list(get_relationships())
        discovered = []

        for rel in rels:
            server = create_or_update_server(user, rel)
            discovered.append(server)

        prune_old_servers(user, discovered)


if __name__ == "__main__":
    setup_db()
    add_relationships()
