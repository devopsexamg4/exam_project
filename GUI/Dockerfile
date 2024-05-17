FROM python:3.12.2-slim
# install requirements
RUN pip install --upgrade pip
COPY ./requirements.txt .
COPY ../IMAGE_BUILDER/requirements.txt ./pod_req.txt
RUN pip install -r requirements.txt
RUN pip install -r pod_req.txt
# install cron to setup scheduled tasks
RUN apt-get update \
    && apt-get --no-install-recommends install -y cron \
    && apt-get clean
# copy files into container
COPY ./UI /app
COPY .env.prod /app/.env
COPY ../IMAGE_BUILDER/kaniko.yml /app/frontend/img/kaniko.yml 
COPY ../IMAGE_BUILDER/podmanager.py /app/frontend/img/podmanager.py
COPY ../IMAGE_BUILDER/__init__.py /app/frontend/img/__init__.py

# read and set secrets
RUN --mount=type=secret,id=secret_1 \
    sed -i "s|SECRET_KEY=|SECRET_KEY=$(cat /run/secrets/secret_1)|" /app/.env
RUN --mount=type=secret,id=secret_2 \
    sed -i "s|DEBUG=|DEBUG=$(cat /run/secrets/secret_2)|" /app/.env
RUN --mount=type=secret,id=secret_3 \
    sed -i "s|ALLOWED_HOSTS=|ALLOWED_HOSTS=$(cat /run/secrets/secret_3)|" /app/.env
RUN --mount=type=secret,id=secret_4 \
    sed -i "s|SU_PASSWORD=|SU_PASSWORD=$(cat /run/secrets/secret_4)|" /app/.env
RUN --mount=type=secret,id=secret_5 \
    sed -i "s|SU_USER=|SU_USER=$(cat /run/secrets/secret_5)|" /app/.env
RUN --mount=type=secret,id=secret_6 \
    sed -i "s|SU_EMAIL=|SU_EMAIL=$(cat /run/secrets/secret_6)|" /app/.env
RUN --mount=type=secret,id=secret_7 \
    sed -i "s|CSRF_TRUSTED=|CSRF_TRUSTED=$(cat /run/secrets/secret_7)|" /app/.env
RUN --mount=type=secret,id=secret_8 \
    sed -i "s|DB_ENGINE=|DB_ENGINE=$(cat /run/secrets/secret_8)|" /app/.env
RUN --mount=type=secret,id=secret_9 \
    sed -i "s|DB_USERNAME=|DB_USERNAME=$(cat /run/secrets/secret_9)|" /app/.env
RUN --mount=type=secret,id=secret_10 \
    sed -i "s|DB_PASSWORD=|DB_PASSWORD=$(cat /run/secrets/secret_10)|" /app/.env
RUN --mount=type=secret,id=secret_11 \
    sed -i "s|DB_HOST=|DB_HOST=$(cat /run/secrets/secret_11)|" /app/.env
RUN --mount=type=secret,id=secret_12 \
    sed -i "s|DB_PORT=|DB_POR=$(cat /run/secrets/secret_12)|" /app/.env
RUN --mount=type=secret,id=secret_13 \
    sed -i "s|CON_STORE=|CON_STORE=$(cat /run/secrets/secret_13)|" /app/.env

# COPY .env /app/.env

# create directories for logs
RUN mkdir -p /var/log/gunicorn/
RUN mkdir -p /var/run/gunicorn/
# change active directory
WORKDIR /app
# run django commands and start the application
RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "sh","./entrypoint.sh" ]
