# FROM python:3.7
FROM tiangolo/uwsgi-nginx-flask:python3.7
#FROM tiangolo/meinheld-gunicorn-flask:python3.7
LABEL maintainer="Sam Gabrail"
ENV LISTEN_PORT=80
# ENV UWSGI_INI uwsgi.ini
# ENV STATIC_URL /app/static
# EXPOSE 5000
# WORKDIR /app
COPY ./src /app
RUN apt-get update && pip install -r requirements.txt
#CMD [ "python", "-u", "app.py" ]