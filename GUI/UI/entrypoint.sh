#!/bin/bash

export $(grep -v '^#' .env | xargs)
# Iterate over all environment variables and strip '\r' and '\n' characters
for var in $(compgen -e); do
    export $var=$(echo -n "${!var}" | tr -d '\r\n')
done

service cron start

python manage.py collectstatic --no-input
python manage.py makemigrations --no-input
python manage.py migrate --no-input

DJANGO_SUPERUSER_PASSWORD=$SU_PASSWORD python manage.py createsuperuser --username $SU_USER --email $SU_EMAIL --noinput

python manage.py crontab add


gunicorn -c config/gunicorn/conf.py

# python manage.py runserver 0.0.0.0:8000