FROM python:3.8.7 AS builder

COPY requirements.txt /requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r /requirements.txt

RUN yum --disablerepo=* --enablerepo="epel" && \
    yum update && \
    yum clean all -y

FROM python:3.8.7-alpine3.12 as runner
COPY --from=builder /venv /venv
COPY --from=builder ./src /app