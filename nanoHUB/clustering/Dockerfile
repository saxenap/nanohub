ARG py_version=3.8

FROM python:${py_version} AS python-image
LABEL maintainer="PRAVEEN SAXENA"

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

RUN set -xe \
    && apt-get -y update \
    && apt-get -y clean autoclean autoremove \
    && rm -fr /var/lib/apt/lists/{apt,dpkg,cache,log} /tmp/* /var/tmp/* \
    && apt-get install -y --no-install-recommends \
    && apt-get install -y rsyslog \
    && apt-get install -y python3-pip cron \
    && pip install --upgrade pip --upgrade setuptools --upgrade wheel

RUN groupadd --gid 1000 user && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash user
RUN mkdir /home/user/app
RUN cd /home/user/app && \
    pip install pipenv

COPY Pipfile /home/user
RUN pipenv lock --pre --clear
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile

COPY ./ /home/user/app

RUN chown -R "1000:1000" /home/user

USER user
WORKDIR /home/user/app
#ENTRYPOINT ["./.venv/bin/python3", "/app/hello-world.py"]