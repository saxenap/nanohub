FROM ubuntu:latest as base-image
LABEL maintainer="saxep01@gmail.com"
LABEL authors="Praveen Saxena"
ARG APP_NAME
ENV APP_NAME=${APP_NAME}
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
RUN echo "NB_USER_DIR=${NB_USER_DIR}" >> /etc/environment
ARG APP_DIR_NAME
ENV APP_DIR="${NB_USER_DIR}/${APP_DIR_NAME}"
RUN echo "APP_DIR=${APP_DIR}" >> /etc/environment
ENV VIRTUAL_ENV=${NB_USER_DIR}/venv
RUN echo "VIRTUAL_ENV=${VIRTUAL_ENV}" >> /etc/environment
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
RUN sed -i '/PATH/c\' /etc/environment \
    && echo "PATH=${PATH}" >> /etc/environment
ENV PYTHONPATH="${APP_DIR}:$PYTHONPATH"
RUN echo "PYTHONPATH=${PYTHONPATH}" >> /etc/environment
ARG LANG
ENV LANG=${LANG}
ARG LC_ALL
ENV LC_ALL=${LC_ALL}
ARG LOCALE
ENV LOCALE=${LOCALE}
ARG DEBIAN_FRONTEND=noninteractive
RUN set -x \
    && build_deps=' \
        build-essential \
    ' \
    && editors=' \
        nano vim \
    ' \
    && pipeline_deps=' \
        cron \
        rsyslog \
        supervisor \
        systemd \
    ' \
    && cartopy_deps=' \
        pkg-config \
        libtiff-dev libsqlite3-dev libproj-dev proj-data proj-bin \
        libgeos-dev \
        ffmpeg \
        libgdal-dev \
    ' \
    && jupyter_deps=' \
        nodejs \
        texlive-xetex \
        texlive-xetex \
        texlive-latex-base \
        texlive-fonts-recommended \
        texlive-latex-recommended \
        texlive-plain-generic \
        texlive-latex-extra \
        pandoc \
    ' \
    && python_deps=' \
        python3-dev \
        python3-venv \
        python3-pip \
        python3-wheel \
    ' \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        $build_deps \
        wget curl git \
        openssh-server \
        $editors \
        sudo \
        locales \
        $pipeline_deps \
#        $cartopy_deps \
        $python_deps \
    \
    && curl -sL https://deb.nodesource.com/setup_16.x -o nodesource_setup.sh \
    && bash nodesource_setup.sh \
    && apt-get install -y --no-install-recommends \
        $jupyter_deps \
    \
    && locale-gen en_US \
    && locale-gen ${LOCALE} \
    && update-locale \
    \
    && useradd -l -m -s /bin/bash -N -u "${NB_UID}" "${NB_USER}" \
    && echo '%sudo ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers \
    && sed -i 's/#\?\(PerminRootLogin\s*\).*$/\1 yes/' /etc/ssh/sshd_config \
    && sed -i 's/#\?\(PermitEmptyPasswords\s*\).*$/\1 yes/' /etc/ssh/sshd_config \
    && cp /root/.bashrc ${NB_USER_DIR}/ \
    && mkdir ${APP_DIR} \
    && chown -R --from=root ${NB_USER} ${APP_DIR} \
    && mkdir ${VIRTUAL_ENV} \
    && chown -R --from=root ${NB_USER} ${VIRTUAL_ENV} \
    \
    && pip3 install --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir pipenv \
    \
    && rm -r /var/lib/apt/lists/*


FROM base-image AS cartopy-image
WORKDIR ${NB_USER_DIR}
RUN curl https://download.osgeo.org/geos/geos-3.9.1.tar.bz2 --output geos.tar.bz2 \
    && mkdir geos \
    && tar xjf geos.tar.bz2 -C geos --strip-components=1 \
    && cd geos \
    && ./configure && make \
    && make install
RUN cd ${NB_USER_DIR} \
    && curl https://pkgconfig.freedesktop.org/releases/pkg-config-0.29.2.tar.gz --output pkgconfig.tgz \
    && mkdir pkgconfig \
    && tar -zxf pkgconfig.tgz -C pkgconfig --strip-components=1 \
    && cd pkgconfig \
    && ./configure --with-internal-glib && make  \
    && make install
RUN cd ${NB_USER_DIR} \
    && curl http://download.osgeo.org/libtiff/tiff-4.0.9.tar.gz --output tiff.tar.gz \
    && mkdir tiff \
    && tar xvfz tiff.tar.gz -C tiff --strip-components=1 \
    && cd tiff \
    && ./configure && make \
    &&  make install \
    &&  ln -s /usr/local/libtiff/lib/pkgconfig/libtiff-4.pc /usr/local/lib/pkgconfig/
RUN cd ${NB_USER_DIR} \
    && curl https://download.osgeo.org/proj/proj-8.1.1.tar.gz --output proj.tar.gz \
    && mkdir proj \
    && tar xzf proj.tar.gz -C proj --strip-components=1 \
    && cd proj/data \
    && curl https://download.osgeo.org/proj/proj-data-1.7.tar.gz --output proj-data.tar.gz \
    && tar xzf proj-data.tar.gz \
    && cd .. \
    && ./configure SQLITE3_LIBS=-lsqlite3 && make \
    && make install
RUN cd ${NB_USER_DIR} \
    && curl http://download.osgeo.org/gdal/CURRENT/gdal-3.3.2.tar.gz --output gdal.tar.gz \
    && mkdir gdal \
    && tar xzf gdal.tar.gz -C gdal --strip-components=1 \
    && cd gdal \
    && ./configure && make \
    && make install


FROM cartopy-image AS nltk-image
WORKDIR ${APP_DIR}
RUN pip3 install wheel \
    && pip3 install --upgrade pip setuptools wheel \
    && pip3 install nltk \
    && python3 -m nltk.downloader -d ${APP_DIR}/nltk_data all


FROM cartopy-image AS packages-image
WORKDIR ${APP_DIR}
COPY Pipfile .
COPY Pipfile.lock .
RUN python3 -m venv ${VIRTUAL_ENV} \
    && pip3 install wheel \
    && pip3 install --upgrade pip setuptools wheel \
    && pipenv lock -r > requirements.txt \
    && pip3 install --no-cache-dir -r requirements.txt \
    && chown -R --from=root ${NB_USER} ${VIRTUAL_ENV}


FROM packages-image AS copied-packages-image
WORKDIR ${APP_DIR}
COPY --from=nltk-image --chown=${NB_UID}:${NB_GID} ${APP_DIR}/nltk_data ${VIRTUAL_ENV}/nltk_data
COPY --from=packages-image --chown=${NB_UID}:${NB_GID} ${VIRTUAL_ENV} ${VIRTUAL_ENV}


FROM copied-packages-image AS jupyter-image
WORKDIR ${APP_DIR}
USER ${NB_USER}
ARG JUPYTERLAB_SETTINGS_DIR=${NB_USER_DIR}/.jupyter
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
RUN jupyter contrib nbextension install --user \
    && jupyter labextension install jupyterlab-topbar-extension \
    && jupyter nbextensions_configurator enable --user \
    && jupyter-nbextension install rise --py --sys-prefix \
    && jupyter-nbextension enable rise --py --sys-prefix \
    && jupyter nbextension enable splitcell/splitcell \
    && jupyter notebook --generate-config \
    && sed -i -e "/c.NotebookApp.token/ a c.NotebookApp.token = ''" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py \
    && sed -i -e "/c.NotebookApp.password/ a c.NotebookApp.password = u'sha1:617c4d2ee1f8:649466c78798c3c021b3c81ce7f8fbdeef7ce3da'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py  \
    && sed -i -e "/allow_root/ a c.NotebookApp.allow_root = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py  \
    && sed -i -e "/c.NotebookApp.custom_display_url/ a c.NotebookApp.custom_display_url = '${JUPYTER_DISPLAY_URL}'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py  \
    && sed -i -e "/c.NotebookApp.ip/ a c.NotebookApp.ip = '${JUPYTER_IP_ADDRESS}'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py  \
    && sed -i -e "/open_browser/ a c.NotebookApp.open_browser = False" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py  \
    && sed -i -e "/c.NotebookApp.disable_check_xsrf/ a c.NotebookApp.disable_check_xsrf = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py  \
    && sed -i -e "/c.ContentsManager.allow_hidden/ a c.ContentsManager.allow_hidden = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py  \
    && sed -i -e "/c.NotebookApp.allow_remote_access/ a c.NotebookApp.allow_remote_access = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py  \
    && sed -i -e "/c.NotebookApp.allow_origin/ a c.NotebookApp.allow_origin = '${ORIGIN_IP_ADDRESS}'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py  \
    && sed -i -e "/c.LabBuildApp.dev_build/ a c.LabBuildApp.dev_build = False" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py \
    && echo '{ "@jupyterlab/notebook-extension:tracker": { "recordTiming": true } }' >> ${VIRTUAL_ENV}/share/jupyter/lab/settings/overrides.json
#RUN jupyter contrib nbextension install --user && \
#    jupyter nbextension enable execute_time/main
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


FROM cartopy-image AS src-image
WORKDIR ${APP_DIR}
COPY . .


FROM jupyter-image AS dev-image
WORKDIR ${NB_USER_DIR}
COPY --from=src-image --chown=${NB_UID}:${NB_GID} ${APP_DIR}/ ${APP_DIR}/
RUN pip3 install ${APP_DIR}
USER root
RUN ln -s ${VIRTUAL_ENV}/bin/nanoHUB /usr/local/bin/nanoHUB \
    && ln -s ${VIRTUAL_ENV}/bin/nanohub /usr/local/bin/nanohub
USER ${NB_USER}
RUN . ${VIRTUAL_ENV}/bin/activate
VOLUME ${APP_DIR}


FROM dev-image AS scheduler-image
USER root
WORKDIR ${APP_DIR}
RUN printf '[supervisord] \nnodaemon=true \n\n\n' >> /etc/supervisor/conf.d/supervisord.conf
RUN printf "[program:cron] \ncommand = cron -f -L 2 \nstartsecs = 0 \nuser = root \nautostart=true \nautorestart=true \nstdout_logfile=/dev/stdout \nredirect_stderr=true \n\n\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN printf "[program:rsyslog] \ncommand = service rsyslog start \nuser = root \nautostart=true \nautorestart=true \nredirect_stderr=true \n\n\n" >> /etc/supervisor/conf.d/supervisord.conf
RUN sed -i '/imklog/s/^/#/' /etc/rsyslog.conf
ARG PAPERTRAIL_URL
ENV PAPERTRAIL_URL=${PAPERTRAIL_URL}
RUN echo "*.*       @${PAPERTRAIL_URL}" >> /etc/rsyslog.conf
WORKDIR ${APP_DIR}
RUN cat ${APP_DIR}/nanoHUB/.env >> /etc/environment
#RUN echo "PATH=${PATH}" >> ${APP_DIR}/cron_tasks \
#    && echo "* * * * *  echo Heartbeat Check" >> ${APP_DIR}/cron_tasks \
#    && echo "* * * * *  make -f ${APP_DIR}/tasks.mk test" >> ${APP_DIR}/cron_tasks \
#    && echo "0 */12 * * *  make -f ${APP_DIR}/tasks.mk execute" >> ${APP_DIR}/cron_tasks \
#    && crontab -u ${NB_USER} ${APP_DIR}/cron_tasks


#    0 */12 * * *  make -f tasks.mk execute
