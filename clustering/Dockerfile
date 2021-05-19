ARG py_version=3.8

FROM python:${py_version} AS python-image

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

RUN set -xe \
    && apt-get -y update \
    && apt-get install -y --no-install-recommends \
    && apt-get install -y python3-pip \
    && pip install --upgrade pip --upgrade setuptools --upgrade wheel \
    && pip install pipenv
COPY Pipfile* .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile
COPY . /app/

ENTRYPOINT ["./.venv/bin/python3", "/app/hello-world.py"]
CMD tail -f /dev/null