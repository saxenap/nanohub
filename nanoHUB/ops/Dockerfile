FROM ubuntu:latest AS vars-image
ARG CPUS=2
ARG GDAL_VERSION="3.4.0"
ARG GEOS_VERSION="3.10.1"
ARG PROJ_VERSION="8.1.1"
ARG DEBIAN_FRONTEND=noninteractive
ENV LOCALE="en_US.UTF-8"
RUN apt-get update -y \
    && set -x \
    && cartopy_deps=' \
        cmake build-essential ca-certificates pkg-config \
        wget \
        libcurl4-openssl-dev \
        libtiff-dev \
        libjpeg-dev \
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
RUN wget \
    http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz \
    && tar -xvzf gdal-${GDAL_VERSION}.tar.gz \
    && cd gdal-${GDAL_VERSION} || exit \
    && ./configure --with-proj=/usr/local --with-python=/usr/bin/python3 --with-local=/usr/local --with-cpp14 --with-geos=yes \
    && make -j${CPUS}  &&  sudo make install  &&  sudo ldconfig \
    && cd .. && rm -rf gdal-${GDAL_VERSION}
ENV CPLUS_INCLUDE_PATH="/usr/include/gdal:$CPLUS_INCLUDE_PATH"
ENV C_INCLUDE_PATH="/usr/include/gdal:$C_INCLUDE_PATH"
ENV LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
RUN pip3 install --no-cache-dir \
    GDAL==${GDAL_VERSION}