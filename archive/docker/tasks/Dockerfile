ARG py_version=3.8

FROM python:${py_version} AS python-image
LABEL maintainer="PRAVEEN SAXENA"

RUN apt-get update && \
    apt-get install -y make && \
    apt-get install -y git && \
    pip install --upgrade pip --upgrade setuptools --upgrade wheel && \
    pip install papermill newrelic && \
    pip install ipykernel && \
    python3 -m ipykernel install --user

COPY ./docker/tasks/Makefile .
COPY ./docker/tasks/notebook_executor.py ./app/

COPY . ./app/
