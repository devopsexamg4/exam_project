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
## Deploying the entire project on google cloud
1. Use terraform to deploy on google cloud
1. Go to `terraform` directory
    2. Create a file `credentials.json` storing your google cloud service account credentials
    2. (optional) Create a file `secrets.json` storing all the secrets described in the next sections
    2. In `setup.sh` set ZONE and PROJECT_ID
    2. Execute `setup.sh clustername namespace`
        3. If a `secrets.json` is not found the script will ask for the values

### Deploying the entire project on another cloud provider
To deploy on a generic cloud 2 options exist:
    - Deploy the services individually as desribed below</br>
    - Modify the files in the `terraform` directory according to the documentation provided by [hashicorp](https://registry.terraform.io/namespaces/hashicorp)</br>

---
## Deploying a service by itself
### Deploying the reverse proxy
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

### Deploying the database
1. Set value for environment variables listed in `DB/.env`
    - POSTGRES_USER: The username for the database
    - POSTGRES_PASSWORD: The password for the database
    - POSTGRES_DB: The name of the database
1. Build the image defined in `DB/Dockerfile`
1. Push the image to your container registry
1. In the file `MANIFESTS/04-db.yml` set the image to be the one just build
1. Apply `MANIFESTS/04-db.yml` to your kubernetes cluster

### Building and deploying the GUI
1. Give a value to the environment varibles listed in `GUI/UI/.env.prod`
    - SECRET_KEY: From django [documentation](https://docs.djangoproject.com/en/5.0/topics/signing/) "This value is the key to securing signed data"
    - DEBUG: [Documentation](https://docs.djangoproject.com/en/5.0/ref/settings/#debug)
    - ALLOWED_HOSTS: [Documentation](https://docs.djangoproject.com/en/5.0/ref/settings/#allowed-hosts)
    - CSRF_TRUSTED: [Documentation](https://docs.djangoproject.com/en/5.0/ref/settings/#csrf-trusted-origins)
    - SU_PASSWORD: The password used for the initial admin user
    - SU_USER: Username used for the initial admin user
    - SU_EMAIL: Email address used for the initial admain user
    - DB_ENGINE: The databse engine [Documentation](https://docs.djangoproject.com/en/5.0/ref/databases/)
    - DB_USERNAME: The username for the database
    - DB_PASSWORD: The password for the database
    - DB_HOST: Where the database is hosted
    - DB_PORT: On which port the database can be accessed
    - CON_STORE: URL to a container registry, images for assignments will be pushed to this registry
    - CLUSTER: Boolean to indicate whether or not the application is running in a cluster
    - MEDIA_PATH: The base directory where uploaded files should be saved
1. Build the image defined in `GUI/Dockerfile`
1. Push the image to your container registry
1. In the file `MANIFESTS/05-gui.yml` set the image to be the one just build
1. Apply `MANIFESTS/05-gui.yml` to your kubernetes cluster


### Deploying the API
1. Give a value to the environment varibles listed in `API/app/env.template`
    - SECRET_KEY: Used to sign JWT tokens -[documentation](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#handle-jwt-tokens)
    - CON_STORE: URL to a container registry, images for assignments will be pushed to this registry
    - DB_HOST: Where the database is hosted
    - DB_PORT: on which port the database can be accessed
    - DB_NAME: The name of the database
    - DB_USER: The username for the database
    - DB_PASSWORD: The username for the database
    - ADMIN_USERNAME: Username used for the initial admin user
    - ADMIN_PASSWORD: The password used for the initial admin user
1. Build the image defined in `API/Dockerfile`
1. Push the image to your container registry
1. In the file `MANIFESTS/06-api.yml` set the image to be the one just build
1. Apply `MANIFESTS/06-api.yml` to your kubernetes cluster

---
## But what if I want to run this locally?
<!---
[//]: # ([This](https://youtu.be/Ef9QnZVpVd8?si=GJXBrbplXsq9dCLL)</br>)
-->
Running API in development mode: [Guide](API/README.md)</br>
Running GUI in development mode: [Guide](GUI/README.md)</br>
