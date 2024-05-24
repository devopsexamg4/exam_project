FROM python:3.10

COPY ./app /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

WORKDIR /code

CMD ["fastapi", "run", "main.py", "--proxy-headers","--port", "8000"]