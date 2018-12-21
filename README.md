# pgAdmin4 example for Platform.sh

This project provides a starting point for hosting [pgAdmin4](https://github.com/postgres/pgadmin4) on Platform.sh.

## Variables

The project requires the following variables in the environment:

### `PGADMIN_DEFAULT_EMAIL`

The email of the default pgadmin user.

```sh
platform variable:create --name env:PGADMIN_DEFAULT_EMAIL --value 'brandon@leblanc.codes' --no-wait --yes
```

### `PGADMIN_DEFAULT_PASSWORD`

The password of the default pgadmin user.

```sh
platform variable:create --name env:PLATFORM_DEFAULT_PASSWORD --value 'rrCsdojUzP3jPgs' --sensitive=true --no-wait --yes
```
