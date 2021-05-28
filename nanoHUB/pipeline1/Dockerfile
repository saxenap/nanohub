FROM alpine:latest

RUN apk update && \
    rm -rf /etc/apk/cache && \
    apk add --update --no-cache docker openrc && \
    apk add --no-cache rsyslog && \
    rc-update add docker boot

RUN sed -i '/imklog/s/^/#/' /etc/rsyslog.conf
COPY rsyslog.conf /etc/rsyslog.d/console.conf

ADD crontab /crontab
RUN /usr/bin/crontab /crontab

CMD /usr/sbin/rsyslogd -n & /usr/sbin/crond -f -l 0