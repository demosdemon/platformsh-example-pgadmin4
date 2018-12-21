# pgAdmin4 example for Platform.sh

This project provides a starting point for hosting [pgAdmin4](https://github.com/postgres/pgadmin4) on Platform.sh.

## Variables

The project requires the following variables in the environment:

### `PGADMIN_SETUP_EMAIL`

The email of the default pgadmin user.

```sh
$ platform variable:create --level environment --name env:PGADMIN_SETUP_EMAIL --value brandon@leblanc.codes --no-wait --yes
Creating variable env:PGADMIN_SETUP_EMAIL on the environment master
+----------------+---------------------------+
| Property       | Value                     |
+----------------+---------------------------+
| id             | env:PGADMIN_SETUP_EMAIL   |
| created_at     | 2018-12-21T12:57:56-06:00 |
| updated_at     | 2018-12-21T12:57:56-06:00 |
| name           | env:PGADMIN_SETUP_EMAIL   |
| attributes     | {  }                      |
| value          | brandon@leblanc.codes     |
| is_json        | false                     |
| project        | anbbnlna43gmq             |
| environment    | master                    |
| inherited      | false                     |
| is_enabled     | true                      |
| is_inheritable | true                      |
| is_sensitive   | false                     |
| level          | environment               |
+----------------+---------------------------+
```

### `PGADMIN_SETUP_PASSWORD`

The password of the default pgadmin user.

```sh
$ platform variable:create --level environment --name env:PGADMIN_SETUP_PASSWORD --value AezMm7U9sAfULzq --sensitive=true --no-wait --yes
Creating variable env:PGADMIN_SETUP_PASSWORD on the environment master
+----------------+----------------------------+
| Property       | Value                      |
+----------------+----------------------------+
| id             | env:PGADMIN_SETUP_PASSWORD |
| created_at     | 2018-12-21T12:59:41-06:00  |
| updated_at     | 2018-12-21T12:59:41-06:00  |
| name           | env:PGADMIN_SETUP_PASSWORD |
| attributes     | {  }                       |
| is_json        | false                      |
| project        | anbbnlna43gmq              |
| environment    | master                     |
| inherited      | false                      |
| is_enabled     | true                       |
| is_inheritable | true                       |
| is_sensitive   | true                       |
| level          | environment                |
+----------------+----------------------------+
```
