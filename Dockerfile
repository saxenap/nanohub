FROM ubuntu:latest AS vars-image
LABEL maintainer="saxep01@gmail.com"
LABEL authors="Praveen Saxena"
ARG CPUS
ENV CPUS=${CPUS}
ARG GDAL_VERSION
ENV GDAL_VERSION=${GDAL_VERSION}
ARG GEOS_VERSION
ENV GEOS_VERSION=${GEOS_VERSION}
ARG PROJ_VERSION
ENV PROJ_VERSION=${PROJ_VERSION}


FROM vars-image AS base-image
ARG APP_NAME
ENV APP_NAME=${APP_NAME}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
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
RUN apt-get update -y \
    && set -x \
    && build_deps=' \
        cmake \
        build-essential \
        ca-certificates \
        pkg-config \
        wget curl git \
        nano vim \
    ' \
    && apt-get install -y --no-install-recommends \
        $build_deps \
    \
    && apt-get install -y --no-install-recommends \
        locales \
    && locale-gen en_US \
    && locale-gen ${LOCALE} \
    && update-locale \
    \
    && useradd -l -m -s /bin/bash -N -u "${NB_UID}" "${NB_USER}" \
    && cp /root/.bashrc ${NB_USER_DIR}/ \
    \
    && mkdir ${APP_DIR} \
    && chown -R --from=root ${NB_USER} ${APP_DIR} \
    && mkdir ${VIRTUAL_ENV} \
    && chown -R --from=root ${NB_USER} ${VIRTUAL_ENV} \
    \
    && apt-get install -y --no-install-recommends \
        sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers \
    \
    && apt-get install -y --no-install-recommends \
        openssh-server \
    && sed -i 's/#\?\(PerminRootLogin\s*\).*$/\1 yes/' /etc/ssh/sshd_config \
    && sed -i 's/#\?\(PermitEmptyPasswords\s*\).*$/\1 yes/' /etc/ssh/sshd_config


FROM base-image AS python-image
RUN set -x \
    && python_deps=' \
        python3-dev \
        python3-venv \
        python3-pip \
        python3-wheel \
    ' \
    && pip_deps=' \
        setuptools \
        wheel \
    ' \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        $python_deps \
    && pip3 install wheel \
    && pip3 install --upgrade pip \
        $pip_deps


FROM python-image AS cartopy-image
RUN set -x \
    && cartopy_deps=' \
        libcurl4-openssl-dev \
        libtiff-dev \
        libjpeg libjpeg-dev \
        sqlite3 libsqlite3-dev \
    ' \
    && apt-get install -y --no-install-recommends \
        $cartopy_deps
RUN wget \
    http://download.osgeo.org/geos/geos-${GEOS_VERSION}.tar.bz2 \
    && tar xjf geos-${GEOS_VERSION}.tar.bz2 \
    && cd geos-${GEOS_VERSION} || exit \
    && ./configure --prefix=/usr/local &&  make -j${CPUS} &&  sudo make install && sudo ldconfig \
    && cd .. && rm -rf geos-${GEOS_VERSION}
RUN wget \
    https://github.com/OSGeo/PROJ/releases/download/${PROJ_VERSION}/proj-${PROJ_VERSION}.tar.gz \
    && tar -xvzf proj-${PROJ_VERSION}.tar.gz \
    && cd proj-${PROJ_VERSION} || exit \
    && ./configure --prefix=/usr/local && make -j${CPUS} && sudo make install && make check && sudo ldconfig \
    && cd .. && rm -rf proj-${PROJ_VERSION}
ENV LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
ENV CPPFLAGS="/usr/local/include:$CPPFLAGS"
RUN wget \
    http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz \
    && tar -xvzf gdal-${GDAL_VERSION}.tar.gz \
    && cd gdal-${GDAL_VERSION} || exit \
    && ./configure --with-proj=/usr/local --with-python=/usr/bin/python3 --with-local=/usr/local --with-cpp14 --with-geos=yes \
        --disable-shared --without-libtool --with-libtiff --with-curl --with-openjpeg --with-png \
    && make -j${CPUS}  &&  sudo make install  &&  sudo ldconfig \
    && cd .. && rm -rf gdal-${GDAL_VERSION}
    \
ENV CPLUS_INCLUDE_PATH="/usr/include/gdal:$CPLUS_INCLUDE_PATH"
ENV C_INCLUDE_PATH="/usr/include/gdal:$C_INCLUDE_PATH"
RUN pip3 install --no-cache-dir \
    GDAL==${GDAL_VERSION}


FROM python-image AS nltk-image
WORKDIR ${APP_DIR}
RUN pip3 install nltk \
    && python3 -m nltk.downloader -d ${APP_DIR}/nltk_data popular


FROM cartopy-image as jupyter-deps-image
RUN set -x \
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
    && curl -sL https://deb.nodesource.com/setup_16.x -o nodesource_setup.sh \
    && bash nodesource_setup.sh \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        $jupyter_deps


FROM jupyter-deps-image AS platform-image
WORKDIR ${APP_DIR}
RUN rm -rf /var/lib/apt/lists/*


FROM python-image AS pip-deps-image
WORKDIR ${APP_DIR}


FROM platform-image AS copied-packages-image
USER root
WORKDIR ${APP_DIR}
RUN pip3 install --upgrade pip
COPY --from=nltk-image --chown=${NB_UID}:${NB_GID} ${APP_DIR}/nltk_data ${VIRTUAL_ENV}/nltk_data
COPY requirements.txt .
RUN python3 -m venv ${VIRTUAL_ENV} \
    && pip3 install --no-cache-dir -r requirements.txt \
    && chown -R --from=root ${NB_USER} ${VIRTUAL_ENV}
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
    && jupyter nbextensions_configurator enable --user \
    && jupyter labextension install jupyterlab-topbar-extension \
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
COPY nanoHUB nanoHUB/
COPY setup.py .
COPY pyproject.toml .
USER root
RUN pip3 install . \
    && chown -R --from=root ${NB_USER} ${APP_DIR}


FROM copied-packages-image as dev-image
USER ${NB_USER}
VOLUME ${APP_DIR}
EXPOSE ${JUPYTER_PORT}


FROM dev-image AS scheduler-image
USER root
WORKDIR ${APP_DIR}
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        cron \
        rsyslog \
        supervisor
RUN printf '[supervisord] \nnodaemon=true \n\n\n' >> /etc/supervisor/conf.d/supervisord.conf \
    && printf "[program:cron] \ncommand = cron -f -L 2 \nstartsecs = 0 \nuser = root \nautostart=true \nautorestart=true \nstdout_logfile=/dev/stdout \nredirect_stderr=true \n\n\n" >> /etc/supervisor/conf.d/supervisord.conf \
    && printf "[program:rsyslog] \ncommand = service rsyslog start \nuser = root \nautostart=true \nautorestart=true \nredirect_stderr=true \n\n\n" >> /etc/supervisor/conf.d/supervisord.conf \
    && sed -i '/imklog/s/^/#/' /etc/rsyslog.conf
ARG PAPERTRAIL_URL
ENV PAPERTRAIL_URL=${PAPERTRAIL_URL}
RUN echo "*.*       @${PAPERTRAIL_URL}" >> /etc/rsyslog.conf
RUN cat ${APP_DIR}/nanoHUB/.env >> /etc/environment
WORKDIR ${APP_DIR}
COPY tasks.mk .
#RUN echo "PATH=${PATH}" >> ${APP_DIR}/cron_tasks \
#    && echo "* * * * *  echo Heartbeat Check" >> ${APP_DIR}/cron_tasks \
#    && echo "* * * * *  make -f ${APP_DIR}/tasks.mk test" >> ${APP_DIR}/cron_tasks \
#    && echo "0 */12 * * *  make -f ${APP_DIR}/tasks.mk execute" >> ${APP_DIR}/cron_tasks \
#    && crontab -u ${NB_USER} ${APP_DIR}/cron_tasks


#    0 */12 * * *  make -f tasks.mk execute
