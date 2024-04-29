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
 
2. `source env/bin/activate` to start python env(ironment)
    - After changes to the requirements
        - `pip install -r requirements.txt` to install dependencies into env
    - After changes to the db
        - `python manage.py makemigrations --no-input`
        - `python manage.py migrate --no-input`
2. `./UI/manage.py runserver` to start development server
