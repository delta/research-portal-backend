# Research Portal Backend

Backend of the Research Portal of NIT Trichy.

# Local development setup
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
python manage.py loaddata api/fixtures/*.json
