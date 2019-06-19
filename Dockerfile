FROM python:3.7.1-stretch
COPY . /flask
WORKDIR /flask
RUN pip install -r requirements.txt
EXPOSE 5000
CMD gunicorn app:app -b0.0.0.0:5000
