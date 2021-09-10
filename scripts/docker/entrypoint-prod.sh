#!/usr/bin/env bash

until psql postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db/${POSTGRES_DB} -c '\l'; do
    echo -e "\e[34m >>> Postgres is unavailable - sleeping \e[97m"
    sleep 1
done

echo "\e[32m >>> Postgres is up - continuing \e[97m"

echo -e "\e[34m >>> Migrating changes \e[97m"
python manage.py migrate --noinput
echo -e "\e[32m >>> migration completed \e[97m"

echo -e "\e[34m >>> Collecting static files \e[97m"
python manage.py collectstatic --noinput
echo -e "\e[32m >>> Static files collected \e[97m"

echo -e "\e[34m >>> Creating superuser \e[97m"
python manage.py createsuperuser --noinput
echo -e "\e[32m >>> Superuser created \e[97m"

exec "$@"