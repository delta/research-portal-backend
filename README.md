# Research Portal Backend

Backend of the Research Portal of NIT Trichy.

# Local development setup

### Prereqs

1. Run rabbitmq

```
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management
```

2. Run [delta/rabbitmq-smtp-mailer](https://github.com/delta/rabbitmq-smtp-mailer) (optional)

### With Docker (Recommended)

1. `cp .env.example .env`
2. `docker-compose -f docker-compose.dev.yml up --build`

Django API is available at localhost:8000

pgAdmin interface is served at localhost:5050 with username admin@admin.com and password admin.

### With virtual environment (For linting and pre-commit hooks)

1. `python -m virtualenv venv`
2. `source ./venv/bin/activate`
3. `pip install -r requirements.txt`
4. `pip install pre-commit pylint && pre-commit install`

## To seed departments, privileges from fixtures

```
python manage.py loaddata api/fixtures/*.json
```

To seed on development docker container

```
docker-compose -f docker-compose.dev.yml exec api python manage.py loaddata api/fixtures/*.json
```
