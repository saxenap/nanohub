FROM alpine:latest AS cron-jobber


RUN apk update && \
    rm -rf /etc/apk/cache && \
    apk add --update --no-cache build-base gcc cmake make docker docker-cli openrc bash && \
    rc-update add docker boot

RUN apk add --no-cache rsyslog rsyslog-tls rsyslog-mmnormalize rsyslog-mmjsonparse \
                       ca-certificates && \
    mkdir /var/spool/rsyslog
RUN wget -O - https://logdog.loggly.com/media/logs-01.loggly.com_sha12.crt >> /etc/ssl/certs/ca-certificates.crt
RUN chmod 755 /etc/ssl/certs/ca-certificates.crt

RUN sed -i '/imklog/s/^/#/' /etc/rsyslog.conf
COPY ./config/rsyslog.conf /etc/rsyslog.d/console.conf
COPY ./config/rsyslog/* /etc/rsyslog.d/

COPY ./docker/cronjobs/Makefile ./app/

ARG ENVVARS_FILEPATH
COPY ./docker/cronjobs/prod.env ./app/.envvars

ARG CRONTAB_FILEPATH
COPY  ./dev.crontab ./app/crontab
RUN /usr/bin/crontab ./app/crontab

CMD /usr/sbin/rsyslogd -n & /usr/sbin/crond -f -l 0