ARG UBUNTU_VERSION
FROM ubuntu:${UBUNTU_VERSION} AS vars-image
LABEL maintainer="saxep01@gmail.com"
LABEL authors="Praveen Saxena"
ARG CPUS


FROM vars-image AS base-image
ARG APP_NAME
ENV APP_NAME=${APP_NAME}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ARG TZ=EST
ENV TZ=${TZ}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
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
        wget curl git sshpass \
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


FROM base-image AS php-image
ARG PHP_VERSION
ENV PHP_VERSION=${PHP_VERSION}
ARG COMPOSER_SIGNATURE
ENV COMPOSER_SIGNATURE=${COMPOSER_SIGNATURE}
RUN apt-get update -y \
    && set -x \
    && php_deps=" \
        libfreetype6-dev \
        libpng-dev \
        libmcrypt-dev \
        php${PHP_VERSION}-dev \
        php${PHP_VERSION}-bcmath \
        php${PHP_VERSION}-common \
        php${PHP_VERSION}-curl \
        php${PHP_VERSION}-gd \
        php${PHP_VERSION}-imagick \
#        php${PHP_VERSION}-json \
        php${PHP_VERSION}-mbstring \
        php${PHP_VERSION}-mysql \
        php-ssh2 \
        php${PHP_VERSION}-opcache \
        php${PHP_VERSION}-zip \
        php-zmq \
    " \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        $php_deps
#RUN echo "extension=zmq.so" > /etc/php/${PHP_VERSION}/mods-available/zmq.ini
WORKDIR ${APP_DIR}
COPY composer.json .
COPY composer.lock .
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
    && php -r "if (hash_file('sha384', 'composer-setup.php') === '${COMPOSER_SIGNATURE}') { echo 'PHP Composer Installer verified'; } else { echo 'PHP Composer Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;" \
    && php composer-setup.php \
    && php -r "unlink('composer-setup.php');" \
    && mv composer.phar /usr/local/bin/composer \
    && ln -s /usr/local/bin/composer /usr/bin/composer \
    && composer install
RUN sed -i -e 's/^error_reporting\s*=.*/error_reporting = E_ALL/' /etc/php/${PHP_VERSION}/cli/php.ini \
    && sed -i -e 's/^display_errors\s*=.*/display_errors = On/' /etc/php/${PHP_VERSION}/cli/php.ini \
    && sed -i -e 's/^zlib.output_compression\s*=.*/zlib.output_compression = Off/' /etc/php/${PHP_VERSION}/cli/php.ini
WORKDIR ${NB_USER_DIR}
RUN curl -s -L -O "https://litipk.github.io/Jupyter-PHP-Installer/dist/jupyter-php-installer.phar" \
    && curl -s -L -O "https://litipk.github.io/Jupyter-PHP-Installer/dist/jupyter-php-installer.phar.sha512" \
    && shasum -s -a 512 -c jupyter-php-installer.phar.sha512


FROM php-image AS python-image
USER root
RUN apt-get update -y \
    && set -x \
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


FROM python-image AS nltk-image
WORKDIR ${APP_DIR}
RUN pip3 install nltk \
    && python3 -m nltk.downloader -d ${APP_DIR}/nltk_data popular


FROM python-image as jupyter-image
RUN apt-get update -y
RUN curl -sL https://deb.nodesource.com/setup_17.x -o nodesource_setup.sh \
    && bash nodesource_setup.sh \
    && apt-get update -y
RUN apt-get update -y \
    && set -x \
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
    && apt-get install -y --no-install-recommends \
        $jupyter_deps


FROM jupyter-image as platform-image
USER root
WORKDIR ${APP_DIR}
RUN apt-get update -y \
    && pip3 install --upgrade pip
COPY requirements.txt .
COPY setup.py .
RUN python3 -m venv ${VIRTUAL_ENV} \
    && pip3 install --no-cache-dir -r requirements.txt \
    && chown -R --from=root ${NB_USER} ${VIRTUAL_ENV}
COPY --from=php-image --chown=${NB_UID}:${NB_GID} /usr/local/bin/composer /usr/local/bin/composer
COPY --from=nltk-image --chown=${NB_UID}:${NB_GID} ${APP_DIR}/nltk_data ${VIRTUAL_ENV}/nltk_data
COPY --from=php-image --chown=${NB_UID}:${NB_GID} ${APP_DIR}/vendor ${APP_DIR}/vendor
RUN composer self-update 1.9.3
USER ${NB_USER}
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
    && jupyter nbextensions_configurator enable --user
RUN jupyter labextension install jupyterlab-topbar-extension \
    && jupyter-nbextension install rise --py --sys-prefix \
    && jupyter-nbextension enable rise --py --sys-prefix \
    && jupyter nbextension enable splitcell/splitcell
ARG JUPYTERLAB_SETTINGS_DIR=${NB_USER_DIR}/.jupyter
RUN jupyter notebook --generate-config
#ARG JUPYTER_TOKEN
#ENV JUPYTER_TOKEN=${JUPYTER_TOKEN}
#RUN sed -i -e "/c.NotebookApp.token/ a c.NotebookApp.token = '${JUPYTER_TOKEN}'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.NotebookApp.token/ a c.NotebookApp.token = ''" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
ARG JUPYTER_PASSWORD
ENV JUPYTER_PASSWORD=${JUPYTER_PASSWORD}
#RUN PASSWORD=$(python3 -c 'from notebook.auth import passwd; print(passwd(passphrase="${JUPYTER_PASSWORD}", algorithm="sha1"))') \
#    && sed -i -e "/c.NotebookApp.password/ a  c.NotebookApp.password = u'${PASSWORD}'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
#RUN #sed -i -e "/c.NotebookApp.password/ a  from notebook.auth import passwd\nimport os\nc.NotebookApp.password = passwd(passphrase=os.getenv('JUPYTER_PASSWORD', algorithm='sha1'))" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.NotebookApp.password/ a c.NotebookApp.password = u'sha1:617c4d2ee1f8:649466c78798c3c021b3c81ce7f8fbdeef7ce3da'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/allow_root/ a c.NotebookApp.allow_root = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
#RUN #sed -i -e "/allow_password_change/ a c.NotebookApp.allow_password_change = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.NotebookApp.custom_display_url/ a c.NotebookApp.custom_display_url = '${JUPYTER_DISPLAY_URL}'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.NotebookApp.ip/ a c.NotebookApp.ip = '${JUPYTER_IP_ADDRESS}'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/open_browser/ a c.NotebookApp.open_browser = False" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.NotebookApp.disable_check_xsrf/ a c.NotebookApp.disable_check_xsrf = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.ContentsManager.allow_hidden/ a c.ContentsManager.allow_hidden = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.FileContentsManager.allow_hidden/ a c.FileContentsManager.allow_hidden = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.NotebookApp.allow_remote_access/ a c.NotebookApp.allow_remote_access = True" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.NotebookApp.allow_origin/ a c.NotebookApp.allow_y \
    origin = '${ORIGIN_IP_ADDRESS}'" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN sed -i -e "/c.LabBuildApp.dev_build/ a c.LabBuildApp.dev_build = False" ${JUPYTERLAB_SETTINGS_DIR}/jupyter_notebook_config.py
RUN echo '{ "@jupyterlab/notebook-extension:tracker": { "recordTiming": true } }' >> ${VIRTUAL_ENV}/share/jupyter/lab/settings/overrides.json
COPY --from=php-image --chown=${NB_UID}:${NB_GID} ${NB_USER_DIR}/jupyter-php-installer.phar ${NB_USER_DIR}/jupyter-php-installer.phar
RUN php ${NB_USER_DIR}/jupyter-php-installer.phar install -n -vvv
COPY nanoHUB nanoHUB/
COPY setup.py .
COPY pyproject.toml .
USER root
#RUN cat ${APP_DIR}/nanoHUB/.env >> /etc/environment
RUN pip3 install . \
    && chown -R --from=root ${NB_USER} ${APP_DIR}


FROM platform-image as remote-image
USER root
RUN cat nanoHUB/.env.dev >> /etc/environment
USER ${NB_USER}
RUN rm -r ${NB_USER_DIR}/nanoHUB/*
COPY nanoHUB/onboarding/README.md ${NB_USER_DIR}/nanoHUB/README.md
COPY nanoHUB/.env.dev ${NB_USER_DIR}/nanoHUB/.env
VOLUME ${APP_DIR}
EXPOSE ${JUPYTER_PORT}


FROM platform-image as dev-image
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
RUN rm -rf ${APP_DIR}/db-reports/*
RUN rm -rf ${APP_DIR}/individual/*
RUN rm -rf ${APP_DIR}/ops/*
RUN rm -rf ${APP_DIR}/raindrop/*
RUN rm -rf ${APP_DIR}/rfm/*
WORKDIR ${APP_DIR}
COPY tasks.mk .
RUN rm -rf /var/lib/apt/lists/*
#RUN echo "PATH=${PATH}" >> ${APP_DIR}/cron_tasks \
#    && echo "* * * * *  echo Heartbeat Check" >> ${APP_DIR}/cron_tasks \
#    && echo "* * * * *  make -f ${APP_DIR}/tasks.mk test" >> ${APP_DIR}/cron_tasks \
#    && echo "0 */12 * * *  make -f ${APP_DIR}/tasks.mk execute" >> ${APP_DIR}/cron_tasks \
#    && crontab -u ${NB_USER} ${APP_DIR}/cron_tasks


#    0 */12 * * *  make -f tasks.mk execute



FROM dev-image as dev-image-with-cartopy
ARG GDAL_VERSION
ARG GEOS_VERSION
ARG PROJ_VERSION
USER root
RUN apt-get update -y \
    && pip3 install --upgrade pip
WORKDIR ${NB_USER_DIR}
RUN \
        apt-get update -y \
        && set -x \
        && cartopy_deps=' \
            libcurl4-openssl-dev \
            libtiff-dev \
            libjpeg-dev \
            sqlite3 libsqlite3-dev \
        ' \
        && set -x \
        && cartopy_pip_deps=' \
            cython \
            ffmpeg-python \
            shapely \
            pyshp \
            pyproj \
            cartopy \
            mkdocs-material \
        ' \
        && apt-get install -y --no-install-recommends \
            $cartopy_deps
RUN  \
        wget http://download.osgeo.org/geos/geos-${GEOS_VERSION}.tar.bz2 \
        && tar xjf geos-${GEOS_VERSION}.tar.bz2 \
        && cd geos-${GEOS_VERSION} || exit \
        && ./configure \
            --prefix=/usr/local \
        &&  make -j${CPUS} &&  sudo make install \
        && sudo ldconfig \
        && cd .. && rm -rf geos-${GEOS_VERSION}
RUN  \
        wget https://github.com/OSGeo/PROJ/releases/download/${PROJ_VERSION}/proj-${PROJ_VERSION}.tar.gz \
        && tar -xvzf proj-${PROJ_VERSION}.tar.gz \
        && cd proj-${PROJ_VERSION} || exit \
        && ./configure \
            --prefix=/usr/local \
        && make -j${CPUS} && sudo make install \
        && make check \
        && sudo ldconfig \
        && cd .. && rm -rf proj-${PROJ_VERSION}
RUN  \
        wget http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz \
        && tar -xvzf gdal-${GDAL_VERSION}.tar.gz \
        && cd gdal-${GDAL_VERSION} || exit \
        && ./configure \
            --with-proj=/usr/local \
            --with-python=/usr/bin/python3 \
            --with-local=/usr/local \
            --with-cpp14 \
            --with-geos=yes \
        && make -j${CPUS}  &&  sudo make install  \
        &&  sudo ldconfig \
        && cd .. && rm -rf gdal-${GDAL_VERSION}
ENV CPLUS_INCLUDE_PATH="/usr/include/gdal:$CPLUS_INCLUDE_PATH"
ENV C_INCLUDE_PATH="/usr/include/gdal:$C_INCLUDE_PATH"
ENV LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
WORKDIR ${APP_DIR}
USER ${NB_USER}
RUN pip3 install --no-cache-dir GDAL==${GDAL_VERSION}
RUN pip3 install $cartopy_pip_deps
VOLUME ${APP_DIR}
EXPOSE ${JUPYTER_PORT}