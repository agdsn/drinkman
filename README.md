# Drinkman
Drinkman is the drink and snack management software of the AG DSN.

The software is meant to be used with a touchscreen.

The main features are:
- User accounts with images and log
- Items with price and image
- Item stocks for multiple locations
- Deposit money
- Cancel transactions a short period after executing
- Responsive design

There are [Screenshots](https://imgur.com/a/uq9FOKB) available.

## Developement setup
Drinkman is built with Django.

The developement setup can be used with a venv.

- Create venv
- Install requirements.txt as venv
- Run `source .devenv`
- Run `./manage.py runserver 0.0.0.0:8000` in venv

The `manage.py` file can be used as follows

- `source venv/bin/activate`
- `source .devenv`
- `./manage.py <command>`

Replace `<command>` with:

***

**Creating migrations**

`makemigrations`

**Running migrations**

`migrate`

**Create superuser account**

`createsuperuser`

***

The admin interface can be accessed at `/admin`.

## Deployment
Drinkman can be deployed with docker-compose using uWSGI. This can be done with the command:

`docker-compose up -d`
 
You can insert database details and secrets with a `docker-compose.override.yml`.
