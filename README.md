# DM885 - Microservices and Dev(sec)ops
# Final project
# Group 4

# A map of the repo
### i.e. What goes where
- [Configuration of the database -> DB](DB)
- [Code for the GUI service build with django -> GUI](GUI)
- [Code for the API service build with FastAPI -> API](API)
- [Manifests for the deployment of the system -> MANIFESTS](MANIFESTS)
- [Python helper module to interact with the cluster -> IMAGE_BUILDER](IMAGE_BUILDER)

# A guide to deployment
## Deploying the reverse proxy
1. Configure your certificate resolver ([Documentation](https://doc.traefik.io/traefik/https/acme/#providers))
    - In `MANIFESTS/02-traefik.yml` set:
        - your email on line 64 (`- --certificatesresolvers.myresolver.acme.email=<your email>`)
        - your provider on line 66 (`- --certificatesresolvers.myresolver.acme.dnschallenge.provider=<provider code>`)
        - set required environment variables as specified by the linked documentation (starting at line 84)
1. Configure domains ([Documentation](https://doc.traefik.io/traefik/https/acme/#configuration-examples))
    - in `MANIFESTS/03-ingressroutes.yml` set:
        - `spec.routes.match`
        - `spec.tls.domains.main`
        - (optional) `spec.tls.domains.sans`
1. Apply manifests to your kubernetes cluster
    - `MANIFESTS/00-rdef.yml`
    - `MANIFESTS/01-rbac.yml`
    - `MANIFESTS/02-traefik.yml`
    - `MANIFESTS/03-ingressroutes.yml`

## Deploying the database

## Deploying the API

## Building and deploying the GUI
1. Give a value to the secrects in `GUI/UI/.env.prod`
    - SECRET_KEY: from django [documentation](https://docs.djangoproject.com/en/5.0/topics/signing/) "This value is the key to securing signed data"
    - DEBUG: [Documentation](https://docs.djangoproject.com/en/5.0/ref/settings/#debug)
    - ALLOWED_HOSTS: [Documentation](https://docs.djangoproject.com/en/5.0/ref/settings/#allowed-hosts)
    - CSRF_TRUSTED: [Documentation](https://docs.djangoproject.com/en/5.0/ref/settings/#csrf-trusted-origins)
    - SU_PASSWORD: The password used for the initial admin user
    - SU_USER: Username used for the initial admin user
    - SU_EMAIL: Email address used for the initial admain user
    - DB_ENGINE: The databse engine [Documentation](https://docs.djangoproject.com/en/5.0/ref/databases/)
    - DB_USERNAME: the username for the database
    - DB_PASSWORD: the password for the database
    - DB_HOST: Where the database is hosted
    - DB_PORT: on which port the database can be accessed
    - CON_STORE: url to a container registry, images for assignments will be pushed to this registry
1. Build the image defined in `GUI/Dockerfile`
1. Push the image to your container registry
1. In the file `MANIFESTS/04-gui.yml` set the image to be the one just build
1. Apply `MANIFESTS/04-gui.yml` to your kubernetes cluster



---
## But what if I want to run this locally?
[This](https://youtu.be/Ef9QnZVpVd8?si=GJXBrbplXsq9dCLL)</br>
Running API in development mode: ![Guide](API/README.md)</br>
Running GUI in development mode: ![Guide](GUI/README.md)</br>
