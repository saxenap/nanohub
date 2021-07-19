FROM ubuntu:latest as base-image
LABEL maintainer="saxep01@gmail.com"
LABEL authors="Praveen Saxena"
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV TZ=America/Indiana/Indianapolis
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    sudo
ARG BUILD_WITH_JUPYTER=1
ENV BUILD_WITH_JUPYTER=${BUILD_WITH_JUPYTER}
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
RUN useradd -l -m -s /bin/bash -N -G sudo -u "${NB_UID}" "${NB_USER}"  && \
    echo '%sudo ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers && \
    cp /root/.bashrc ${NB_USER_DIR}/ && \
    chown -R --from=root ${NB_USER} ${NB_USER_DIR}
USER ${NB_USER}
WORKDIR ${APP_DIR}
ENV VIRTUAL_ENV=${NB_USER_DIR}/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN sudo apt-get install -y --no-install-recommends \
    build-essential \
    wget curl git \
    openssh-server \
    nano vim \
    python3-dev python3-venv python3-pip



FROM base-image AS build-image
USER ${NB_USER}
WORKDIR ${APP_DIR}
RUN pip3 install --upgrade pip --upgrade setuptools --upgrade wheel \
    && pip3 install --no-cache-dir pipenv
RUN python3 -m venv ${VIRTUAL_ENV}
COPY Pipfile .
RUN pipenv lock -r > requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
COPY nanoHUB/.env ./nanoHUB/.env
RUN pip3 install .
USER root
RUN chown -R --from=root ${NB_USER} ${APP_DIR}
USER ${NB_USER}



FROM base-image AS code-base-image
USER ${NB_USER}
COPY --from=build-image --chown=${NB_UID}:${NB_GID} ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=build-image --chown=${NB_UID}:${NB_GID} ${APP_DIR} ${APP_DIR}
WORKDIR ${APP_DIR}



#FROM base-image AS with-jupyter-0
#USER ${NB_USER}
#COPY --from=build-image --chown=${NB_UID}:${NB_GID} ${VIRTUAL_ENV} ${VIRTUAL_ENV}
#COPY --from=build-image --chown=${NB_UID}:${NB_GID} ${APP_DIR} ${APP_DIR}
#WORKDIR ${APP_DIR}



FROM code-base-image AS jupyter-image
USER root
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow
RUN apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-recommended \
    texlive-plain-generic \
    texlive-latex-extra \
    pandoc
USER ${NB_USER}
WORKDIR ${APP_DIR}
ARG JUPYTER_PORT=8888
ENV JUPYTER_PORT=${JUPYTER_PORT}
RUN jupyter notebook --generate-config && \
    sed -i -e "/allow_root/ a c.NotebookApp.allow_root = True" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.ip/ a c.NotebookApp.ip = '*'" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/open_browser/ a c.NotebookApp.open_browser = False" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.disable_check_xsrf/ a c.NotebookApp.disable_check_xsrf = True" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.ContentsManager.allow_hidden/ a c.ContentsManager.allow_hidden = True" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.allow_remote_access/ a c.NotebookApp.allow_remote_access = True" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.allow_origin/ a c.NotebookApp.allow_origin = ''" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py
RUN if [ -z $BUILD_WITH_JUPYTER=1 ] ; then \
    pip3 install nodeenv && nodeenv -p  && \
    pip3 install jupyterlab_templates && \
    pip3 install --upgrade jupyterthemes  && \
    pip3 install jupyter_contrib_nbextensions && \
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
    jupyter nbextension enable snippets/main && \
    pip3 install qgrid && \
    jupyter nbextension enable --py --sys-prefix qgrid && \
    pip3 install RISE && \
    pip3 install jupyterlab_executor && \
    pip3 install jupyterlab-quickopen && \
    pip3 install jupyterlab_sql && \
    jupyter serverextension enable jupyterlab_sql --py --sys-prefix && \
    pip3 install jupyterlab-system-monitor && \
    pip3 install jupyterlab-topbar && \
    jupyter labextension install jupyterlab-topbar-text && \
    jupyter labextension install @jupyterlab/toc && \
    pip3 install lckr-jupyterlab-variableinspector && \
    #RUN jupyter labextension install jupyterlab_voyager && \
    pip3 install 'jupyterlab>=3.0.0,<4.0.0a0' jupyterlab-lsp && \
    pip3 install 'python-lsp-server[all]' && \
    jupyter labextension install @krassowski/jupyterlab_go_to_definition && \
    jupyter labextension install @jupyterlab/debugger && \
    jupyter lab build; \
    fi

EXPOSE ${JUPYTER_PORT}



FROM jupyter-image AS dev-image
USER ${NB_USER}
WORKDIR ${APP_DIR}
#CMD jupyter lab



FROM code-base-image AS scheduler-image
USER root
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    gcc \
    make \
    cron \
    rsyslog \
    supervisor
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
COPY nanoHUB/scheduler/rsyslog.conf /etc/rsyslog.conf
COPY nanoHUB/scheduler/syslog.conf /etc/syslog.conf
RUN service rsyslog start
RUN touch /var/log/cron.log
RUN chown -R --from=root ${NB_USER} /var/log/cron.log
ARG CRONTAB_FILE
COPY ${CRONTAB_FILE} ${APP_DIR}/cron_tasks
RUN chown -R --from=root ${NB_USER} ${APP_DIR}/cron_tasks
USER ${NB_USER}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN chmod 0644 ${APP_DIR}/cron_tasks
RUN crontab ${APP_DIR}/cron_tasks
COPY nanoHUB/scheduler/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
WORKDIR ${APP_DIR}

