FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt
COPY ./app /app
