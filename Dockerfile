FROM ubuntu:latest as base-image
LABEL maintainer="saxep01@gmail.com"
LABEL authors="Praveen Saxena"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ARG TZ
ENV TZ=${TZ}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ARG BUILD_WITH_JUPYTER=1
ENV BUILD_WITH_JUPYTER=${BUILD_WITH_JUPYTER}
ARG NB_USER
ARG NB_UID
ARG NB_GID
ENV NB_USER=${NB_USER}
ENV NB_UID=${NB_UID}
ENV NB_GID=${NB_GID}
ARG HOME_DIR_NAME
ENV NB_USER_DIR="/${HOME_DIR_NAME}/${NB_USER}"
ARG APP_DIR_NAME
ENV APP_DIR="${NB_USER_DIR}/${APP_DIR_NAME}"
ENV VIRTUAL_ENV=${NB_USER_DIR}/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN apt-get update -y
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
RUN apt-get install -y --no-install-recommends \
        language-pack-en-base && \
    locale-gen "en_US.UTF-8"


FROM base-image AS user-image
RUN apt-get install -y --no-install-recommends sudo
RUN useradd -l -m -s /bin/bash -N -u "${NB_UID}" "${NB_USER}" && \
    usermod -aG sudo ${NB_USER} && \
    echo '%sudo ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers && \
    cp /root/.bashrc ${NB_USER_DIR}/ && \
    chown -R --from=root ${NB_USER} ${NB_USER_DIR}


FROM user-image AS build-image
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y --no-install-recommends \
        build-essential \
        wget curl git \
        openssh-server \
        nano vim \
        python3-dev python3-venv python3-pip \
        texlive-xetex \
        texlive-latex-base \
        texlive-fonts-recommended \
        texlive-latex-recommended \
        texlive-plain-generic \
        texlive-latex-extra \
        pandoc
RUN pip3 install --upgrade pip --upgrade setuptools --upgrade wheel \
    && pip3 install --no-cache-dir pipenv
RUN python3 -m venv ${VIRTUAL_ENV}


FROM build-image AS packages-image
WORKDIR ${APP_DIR}
RUN python3 -m venv ${VIRTUAL_ENV}
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv lock -r > requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt


FROM build-image AS app-image
WORKDIR ${APP_DIR}
COPY . .
COPY nanoHUB/.env ./nanoHUB/.env


FROM build-image AS code-base-image
USER root
COPY --from=packages-image --chown=${NB_UID}:${NB_GID} ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=app-image --chown=${NB_UID}:${NB_GID} ${APP_DIR} ${APP_DIR}
RUN chown -R ${NB_USER} ${APP_DIR}
USER ${NB_USER}
WORKDIR ${APP_DIR}
RUN pip3 install .


FROM code-base-image AS jupyter-image
USER root
RUN apt install -y nodejs
USER ${NB_USER}
WORKDIR ${APP_DIR}
ARG JUPYTER_PORT=80
ENV JUPYTER_PORT=${JUPYTER_PORT}
ARG ORIGIN_IP_ADDRESS
ENV ORIGIN_IP_ADDRESS=${ORIGIN_IP_ADDRESS}
ARG JUPYTER_IP_ADDRESS
ENV JUPYTER_IP_ADDRESS=${JUPYTER_IP_ADDRESS}
ARG JUPYTER_DISPLAY_IP_ADDRESS
ENV JUPYTER_DISPLAY_IP_ADDRESS=${JUPYTER_DISPLAY_IP_ADDRESS}
ARG JUPYTER_DISPLAY_URL="http://${JUPYTER_DISPLAY_IP_ADDRESS}:${JUPYTER_PORT}"
ENV JUPYTER_DISPLAY_URL=${JUPYTER_DISPLAY_URL}
RUN jupyter notebook --generate-config && \
    sed -i -e "/c.NotebookApp.token/ a c.NotebookApp.token = ''" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.password/ a c.NotebookApp.password = u'sha1:617c4d2ee1f8:649466c78798c3c021b3c81ce7f8fbdeef7ce3da'" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/allow_root/ a c.NotebookApp.allow_root = True" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.custom_display_url/ a c.NotebookApp.custom_display_url = '${JUPYTER_DISPLAY_URL}'" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.ip/ a c.NotebookApp.ip = '${JUPYTER_IP_ADDRESS}'" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/open_browser/ a c.NotebookApp.open_browser = False" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.disable_check_xsrf/ a c.NotebookApp.disable_check_xsrf = True" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.ContentsManager.allow_hidden/ a c.ContentsManager.allow_hidden = True" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.allow_remote_access/ a c.NotebookApp.allow_remote_access = True" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.NotebookApp.allow_origin/ a c.NotebookApp.allow_origin = '${ORIGIN_IP_ADDRESS}'" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py && \
    sed -i -e "/c.LabBuildApp.dev_build/ a c.LabBuildApp.dev_build = False" ${NB_USER_DIR}/.jupyter/jupyter_notebook_config.py
RUN jupyter-nbextension install rise --py --sys-prefix && \
    jupyter-nbextension enable rise --py --sys-prefix
RUN jupyter nbextension enable splitcell/splitcell
#RUN jupyter contrib nbextension install --user && \
#    jupyter nbextension enable codefolding/main && \
#    jupyter nbextension enable table_beautifier/main && \
#    jupyter nbextension enable toc2/main && \
#    jupyter nbextension enable init_cell/main && \
#    jupyter nbextension enable tree-filter/main && \
#    jupyter nbextension enable jupyter_boilerplate/main && \
#    jupyter nbextension enable scroll_down/main && \
#    jupyter nbextension enable notify/main && \
#    jupyter nbextension enable skip-traceback/main && \
#    jupyter nbextension enable move_selected_cells/main && \
#    jupyter nbextension enable livemdpreview/main && \
#    jupyter nbextension enable highlighter/main && \
#    jupyter nbextension enable go_to_current_running_cell/main && \
#    jupyter nbextension enable execute_time/main && \
#    jupyter nbextension enable datestamper/main && \
#    jupyter nbextension enable addbefore/main && \
#    jupyter nbextension enable Hinterland/main && \
#    jupyter nbextension enable snippets/main && \
##    jupyter nbextension enable --py --sys-prefix qgrid && \
##    jupyter serverextension enable jupyterlab_sql --py --sys-prefix && \
#    jupyter nbextension enable --py --sys-prefix widgetsnbextension && \
#    jupyter labextension install --no-build jupyterlab-topbar-text && \
#    jupyter labextension install --no-build @jupyterlab/toc && \
#    jupyter labextension install --no-build @krassowski/jupyterlab_go_to_definition && \
#    jupyter labextension install --no-build @jupyterlab/debugger && \
#    jupyter lab build --dev-build=False;
EXPOSE ${JUPYTER_PORT}


FROM jupyter-image AS dev-image
USER ${NB_USER}
WORKDIR ${APP_DIR}
VOLUME ${APP_DIR}


FROM code-base-image AS scheduler-image
USER root
RUN apt-get install -y --no-install-recommends \
        cron \
        rsyslog \
        supervisor \
        systemd
RUN printf '[supervisord] \nnodaemon=true \n\n\n' >> /etc/supervisor/conf.d/supervisord.conf
RUN printf "[program:cron] \ncommand = cron -f -L 2 \nstartsecs = 0 \nuser = root \nautostart=true \nautorestart=true \nstdout_logfile=/dev/stdout \nredirect_stderr=true \n\n\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN printf "[program:rsyslog] \ncommand = service rsyslog start \nstartsecs = 0 \nuser = root \nautostart=true \nautorestart=true \nredirect_stderr=true \n\n\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN sed -i '/imklog/s/^/#/' /etc/rsyslog.conf
ARG PAPERTRAIL_URL
ENV PAPERTRAIL_URL=${PAPERTRAIL_URL}
RUN echo "*.*       @${PAPERTRAIL_URL}" >> /etc/rsyslog.conf
WORKDIR ${APP_DIR}
ARG CRONTAB_FILE
COPY ${CRONTAB_FILE} ${APP_DIR}/temp
RUN echo "PATH=${PATH}" >> ${APP_DIR}/cron_tasks
RUN echo "HOME=${NB_USER_DIR}" >> ${APP_DIR}/cron_tasks
RUN cat "${APP_DIR}/temp" >> ${APP_DIR}/cron_tasks
RUN crontab -u ${NB_USER} ${APP_DIR}/cron_tasks