#!/bin/bash

export $(grep -v '^#' .env | xargs)


python manage.py collectstatic --no-input
python manage.py makemigrations --no-input
python manage.py migrate --no-input

DJANGO_SUPERUSER_PASSWORD=$SU_PASSWORD python manage.py createsuperuser --username $SU_USER --email $SU_EMAIL --noinput

gunicorn -c config/gunicorn/conf.py

# python manage.py runserver 0.0.0.0:8000