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

The developement setup is built in docker. You can run the developement setup with 

`docker-compose -f docker-compose.dev.yml up -d`.

Some operations must be done within the Docker container. This can be done with 

`docker-compose -f docker-compose.dev.yml run drinkman_dev python3 manag.py <command>`

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
