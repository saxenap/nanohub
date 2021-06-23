FROM ubuntu:latest as base-image
LABEL maintainer="saxep01@gmail.com"
LABEL authors="Praveen Saxena"
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    gcc \
    wget curl git \
    sudo \
    python3-dev python3-venv python3-pip
ARG NB_USER
ARG NB_UID="1000"
ARG NB_GID="100"
ENV NB_USER=${NB_USER}
ENV NB_UID=${NB_UID}
ENV NB_GID=${NB_GID}
ARG HOME_DIR_NAME
ENV NB_USER_DIR="/${HOME_DIR_NAME}/${NB_USER}"
ARG APP_DIR_NAME
ENV APP_DIR="${NB_USER_DIR}/${APP_DIR_NAME}"
RUN useradd -l -m -s /bin/bash -N -u "${NB_UID}" "${NB_USER}" && \
    usermod -aG sudo ${NB_USER} && \
    echo '%sudo ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers && \
    cp /root/.bashrc ${NB_USER_DIR}/ && \
    chown -R --from=root ${NB_USER} ${NB_USER_DIR}
USER ${NB_USER}
WORKDIR ${APP_DIR}
ENV VIRTUAL_ENV=${NB_USER_DIR}/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"



FROM base-image AS build-image
USER root
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential make \
    openssh-server \
    nano vim
RUN pip3 install --upgrade pip --upgrade setuptools --upgrade wheel \
    && pip3 install --no-cache-dir pipenv
USER ${NB_USER}
WORKDIR ${APP_DIR}
RUN python3 -m venv ${VIRTUAL_ENV}
COPY Pipfile* .
RUN pipenv lock -r > requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
RUN pip3 install .
USER root
RUN chown -R --from=root ${NB_USER} ${APP_DIR}
USER ${NB_USER}



FROM base-image AS code-base-image
USER ${NB_USER}
COPY --from=build-image --chown=${NB_UID}:${NB_GID} ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=build-image --chown=${NB_UID}:${NB_GID} ${APP_DIR} ${APP_DIR}
WORKDIR ${APP_DIR}



FROM code-base-image AS jupyter-image
USER ${NB_USER}
WORKDIR ${APP_DIR}
ARG JUPYTER_PORT=8888
ENV JUPYTER_PORT=${JUPYTER_PORT}
RUN pip3 install nodeenv && nodeenv -p
RUN pip3 install jupyterlab_templates && \
    pip3 install --upgrade jupyterthemes
RUN pip3 install jupyter_contrib_nbextensions && \
    jupyter contrib nbextension install --user && \
    jupyter nbextension enable codefolding/main && \
    jupyter nbextension enable table_beautifier/main && \
    jupyter nbextension enable toc2/main && \
    jupyter nbextension enable splitcell/main && \
    jupyter nbextension enable varInspector/main && \
    jupyter nbextension enable init_cell/main && \
    jupyter nbextension enable tree-filter/main && \
    jupyter nbextension enable jupyter_boilerplate/main && \
    jupyter nbextension enable scroll_down/main && \
    jupyter nbextension enable notify/main && \
    jupyter nbextension enable skip-traceback/main && \
    jupyter nbextension enable move_selected_cells/main && \
    jupyter nbextension enable livemdpreview/main && \
    jupyter nbextension enable highlighter/main && \
    jupyter nbextension enable go_to_current_running_cell/main && \
    jupyter nbextension enable execute_time/main && \
    jupyter nbextension enable datestamper/main && \
    jupyter nbextension enable addbefore/main && \
    jupyter nbextension enable Hinterland/main && \
    jupyter nbextension enable snippets/main
RUN pip3 install qgrid && \
    jupyter nbextension enable --py --sys-prefix qgrid
RUN pip3 install RISE
RUN pip3 install jupyterlab_executor
RUN pip3 install jupyterlab-quickopen
RUN pip3 install jupyterlab_sql && \
    jupyter serverextension enable jupyterlab_sql --py --sys-prefix
RUN pip3 install jupyterlab-system-monitor
RUN pip3 install jupyterlab-topbar && \
    jupyter labextension install jupyterlab-topbar-text
RUN pip3 install lckr-jupyterlab-variableinspector
#RUN jupyter labextension install jupyterlab_voyager
RUN pip3 install 'jupyterlab>=3.0.0,<4.0.0a0' jupyterlab-lsp && \
    pip3 install 'python-lsp-server[all]'
RUN jupyter labextension install @krassowski/jupyterlab_go_to_definition
RUN jupyter labextension install @jupyterlab/debugger
RUN jupyter notebook --generate-config && \
    sed -i -e "/allow_root/ a c.NotebookApp.allow_root = True" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.ip/ a c.NotebookApp.ip = '*'" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/open_browser/ a c.NotebookApp.open_browser = False" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py
RUN jupyter lab build
EXPOSE ${JUPYTER_PORT}



FROM jupyter-image AS dev-image
USER ${NB_USER}
WORKDIR ${APP_DIR}

