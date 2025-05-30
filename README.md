# job-finder-django

## Introduction
- use django-ninja, django-ninja-jwt to build a RESTful API Job Finder application
- use django-auth to protect API Docs access
![pic](https://github.com/pingshian0131/job-finder-django/blob/main/static/api_docs_screenshot.png)
- pytest-django for testing, based on API Level testing
- SQlite3 as default database, but can be configured to use Postgres
- JWT authentication for protected API access, such as creating, updating, and deleting jobs

## setup
  - create virtual environment
    - `python -m venv venv`
  - activate virtual environment
    - `source venv/bin/activate` (Linux/Mac)
    - `venv\Scripts\activate` (Windows)
  - install dependencies
    - `pip install -r requirements.txt`
  - create database
    - `python manage.py migrate`
  - insert test data
    - by fixtures
      - `python manage.py loaddata app_job.json`
    - by management command
      - `python manage.py seed_data`
  - run server
    - `python manage.py runserver`

## django-ninja api docs url
  - create superuser
    - `python manage.py createsuperuser`
  - access api docs
    - login with superuser credentials (or any staff user)
    - use `/api/v1/token/pair` to get JWT token
    - click the doc's `Authorize` button and enter the token
    - http://127.0.0.1:8000/api/docs

## test
  1. see current test result from github actions
  2. run tests locally
    - make sure you have a database created and migrated
    - run the following commands in your terminal:
      - run test & coverage
        - `coverage run --source=./app -m pytest ./app/tests/test_apis.py`
      - or test only
        - `pytest ./app/tests/test_apis.py`
      - get report
        - `coverage report --fail-under=90`



## Use Postgres
  - run postgres container
```bash
docker run --name postgres \
-p 5432:5432 \
-e POSTGRES_USER admin \
-e POSTGRES_PASSWORD admin \
-v postgres_data:/var/lib/postgresql/data \
-d postgres:latest
```
  - setup env variables
```text
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=app_db
SQL_USER=admin
SQL_PASSWORD=admin
SQL_HOST=localhost
SQL_PORT=5432
```
  - run migrate
    - `python manage.py migrate`

## CICD
  - use github actions to run blackd format check, tests, and coverage
  - to see the current test result, check the [Actions tab](https://github.com/job-finder-django/actions/)
