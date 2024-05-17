# ui
ui module
## Staring the UI service first time(Hardmode)

1. assuming linux environment with python installed and project has been pulled
1. go to UI directory open terminal
1.	`python -m venv env` to start a virtual python environment
1. `source env/bin/activate` to start python env(ironment)
1. `pip install -r requirements.txt` to install dependencies into env
1. `python manage.py collectstatic --no-input`
1. `python manage.py makemigrations --no-input`
1. `python manage.py migrate --no-input`
1. `python manage.py createsuperuser`
1. `./UI/manage.py runserver` to start development server

## Starting the UI service in development mode
 
1. `source env/bin/activate` to start python env(ironment)
    - After changes to the requirements
        - `pip install -r requirements.txt` to install dependencies into env
    - After changes to the db
        - `python manage.py makemigrations --no-input`
        - `python manage.py migrate --no-input`
1. `./UI/manage.py runserver` to start development server

## Run tests
1. Navigate to the UI directory
2. `./manage.py test` to run all tests

For coverage run
1. `coverage run --source='.' manage.py test` 
1. `coverage report` for a short view in the terminal 
1. `coverage html` to generate a detailed html report, viewable at ./htmlcov/index.html 