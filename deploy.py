#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from config import SQLITE_PATH
from pgadmin import create_app
from pgadmin.model import SCHEMA_VERSION, Server, ServerGroup, User, Version, db
from pgadmin.setup import db_upgrade
from psh import env


def setup_db():
    app = create_app()

    with app.app_context():
        if not os.path.exists(SQLITE_PATH):
            db_upgrade(app)
        else:
            version = Version.query.filter_by(name="ConfigDB").first()
            if version is None:
                os.unlink(SQLITE_PATH)
                db_upgrade(app)
            else:
                schema_version = version.value

                if SCHEMA_VERSION >= schema_version:
                    db_upgrade(app)

                if SCHEMA_VERSION > schema_version:
                    version = Version.query.filter_by(name="ConfigDB").first()
                    version.value = SCHEMA_VERSION
                    db.session.commit()


def get_relationships():
    relationships = env("PLATFORM_RELATIONSHIPS")
    for group, nodes in relationships.items():
        for node in nodes:
            if node["scheme"] == "pgsql":
                yield {
                    "Name": node["cluster"],
                    "Host": node["host"],
                    "Group": group,
                    "Port": node["port"],
                    "Username": node["username"],
                    "Password": node["password"],
                    "SSLMode": "Prefer",
                    "MaintenanceDB": "postgres",
                    "Role": node["path"],
                }


def add_relationships():
    app = create_app()

    with app.app_context():
        userid = env("PGADMIN_SETUP_EMAIL")
        if not userid:
            raise RuntimeError("Expected $PGADMIN_SETUP_EMAIL environment variable.")

        user = User.query.filter_by(email=userid).first()
        if user is None:
            raise RuntimeError(
                "The specified user ID ({}) could not be found.".format(userid)
            )

        rels = list(get_relationships())
        groups = ServerGroup.query.all()

        for rel in rels:
            group_id = -1
            for g in groups:
                if g.name == rel["Group"]:
                    group_id = g.id
                    break

            if group_id == -1:
                new_group = ServerGroup()
                new_group.name = rel["Group"]
                new_group.user_id = userid
                db.session.add(new_group)

                try:
                    db.session.commit()
                except Exception:
                    raise RuntimeError("Error creating server group.")

                group_id = new_group.id
                groups = ServerGroup.query.all()

            new_server = Server()
            new_server.name = rel["Name"]
            new_server.servergroup_id = group_id
            new_server.user_id = userid
            new_server.host = rel["Host"]
            new_server.port = rel["Port"]
            new_server.maintenance_db = rel["MaintenanceDB"]
            new_server.username = rel["Username"]
            new_server.password = rel["Password"]
            new_server.role = rel["Role"]
            new_server.ssl_mode = rel["SSLMode"]

            db.session.add(new_server)

            try:
                db.session.commit()
            except Exception:
                raise RuntimeError("Error creating server.")


if __name__ == "__main__":
    setup_db()
    add_relationships()
