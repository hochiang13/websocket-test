FROM python:3.6-slim

ENV PYTHONUNBUFFERED 0

WORKDIR /k8s_ws

COPY requirements.txt app.py ./
RUN pip install -r requirements.txt

CMD gunicorn -b 0.0.0.0:8080 --worker-class eventlet -w 1 app:app

