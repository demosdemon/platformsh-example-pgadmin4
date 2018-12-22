# pgAdmin4 example for Platform.sh

This project provides a starting point for hosting [pgAdmin4](https://github.com/postgres/pgadmin4) on Platform.sh.

## Variables

The project requires the following variables in the environment:

### `PGADMIN_SETUP_EMAIL`

The email of the default pgadmin user.

```sh
$ platform variable:create --level environment --name env:PGADMIN_SETUP_EMAIL --value brandon@leblanc.codes --no-wait --yes
Creating variable env:PGADMIN_SETUP_EMAIL on the environment master
...
```

### `PGADMIN_SETUP_PASSWORD`

The password of the default pgadmin user.

```sh
$ platform variable:create --level environment --name env:PGADMIN_SETUP_PASSWORD --value AezMm7U9sAfULzq --sensitive=true --no-wait --yes
Creating variable env:PGADMIN_SETUP_PASSWORD on the environment master
...
```

### `GUNICORN_THREADS`

An optional value controlling the number of threads `gunicorn` is allowed to spawn. If not provided, defaults to 25.

Normally on Platform.sh, you would scale your application by adding more workers. However, due to the way pgAdmin4 is implemented it is unable to scale this way. It relies on threads instead. The pertinent details are in the way pgAdmin4 shares SQL connections between requests.

```sh
$ platform variable:create --level environment --name env:GUNICORN_THREADS --value 50 --no-wait --yes
Creating variable env:GUNICORN_THREADS on the environment master
...
```

### `PGADMIN4_SUPPORT_SSH_TUNNEL`

An optional value controlling whether or not to enable output ssh tunnels. If not provided, defaults to `false`.

```sh
$ platform variable:create --level environment --name env:PGADMIN4_SUPPORT_SSH_TUNNEL --value true --no-wait --yes
Creating variable env:PGADMIN4_SUPPORT_SSH_TUNNEL on the environment master
...
```
