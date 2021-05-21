ARG image_version=latest

FROM jupyter/base-notebook:${image_version} AS jupyterbase-image

RUN    pip install --upgrade pip --upgrade setuptools --upgrade wheel \
    && pip install papermill

#CMD jupyter-lab notebook --ip 0.0.0.0 --port 8888 --allow-root

COPY . /home/jovyan/work
