# ui
ui module
## Staring the UI service in development mode first time

1. assuming linux environment with python installed and project has been pulled
1. In the GUI directory open terminal
1.	`python -m venv env` to start a virtual python environment
1. `source env/bin/activate` to activate python env(ironment)
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
        - In some cases where the db has been changed these commands might fail (particulaly when changing or removing existing attributes), if they do the suggested fix is to delete the sqlite db file and all *.py files in GUI/UI/frontend/migrations except \_\_init\_\_.py. Then re-run the previous commands followed by `python manage.py createsuperuser` to rebuild the db and create a superuser.
1. `./UI/manage.py runserver` to start development server

## Run tests
1. Navigate to the UI directory
2. `./manage.py test` to run all tests
