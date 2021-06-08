ARG py_version=3.8

FROM python:${py_version} AS python-image
LABEL maintainer="PRAVEEN SAXENA"

RUN apt-get update && \
    apt-get install -y make && \
    apt-get install -y git && \
    apt-get install -y cron && \
    apt-get install -y rsyslog && \
    pip install --upgrade pip --upgrade setuptools --upgrade wheel && \
    pip install papermill newrelic && \
    pip install ipykernel && \
    python3 -m ipykernel install --user

COPY ./docker/single/Makefile .

COPY $ENVVARS_FILEPATH ./app/.envvars

COPY $CRONTAB_FILEPATH ./app/crontab
RUN /usr/bin/crontab ./app/crontab


COPY . ./app/
CMD rsyslogd -n & cron -f -l 0