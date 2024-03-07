# THE VERY BEST REPO
# For development purposes only
## Staring the UI service first time(Hardmode)

1. assuming linux environment with python installed and project has been pulled
1. go to UI directory open terminal
1.	`python -m venv env` to start a virtual python environment
1. `source env/bin/activate` to start python env(ironment)
1. `pip install -r requirements.txt` to install dependencies into env
1. `./UI/manage.py runserver` to start development server<br>

## Staring the UI service(easy mode)

1. Have docker installed and running
1. run `docker compose build`
1. run `docker compose up -d`
1. open browser to [frontpage](http://localhost:8000)

## link to overleaf
[overleaf doc](https://www.overleaf.com/1442327655stwrrmfrymjv#707254)<br>

## Structure of our project

### environments
- testing på sdu ucloud
- production på google cloud

### Techstack
- primary language: python
- secondary languages: JS, CSS, HTML
- version control: github
- pipeline: github actions
- database: postgresql
- containerisation: docker
- some sort of orchestrator
- webserver: nginx
- GUI: django
- API: FastAPI
- consider rabbitmq for message passing between containers


### pre-work
- user stories
- documentation in README.md
- consider attack vectors

### tasks
- setup pipeline
- tests
- db design
- frontend GUI design

### post work
- group report
- individual reports

### Link to API readme
[Link to API readme](./api/README.md)

