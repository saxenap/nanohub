# Use thick image to build.
FROM python:3.8.7 AS builder

COPY requirements.txt /requirements.txt

RUN set -xe \
    && apt-get -y update \
    && apt-get install -y --no-install-recommends \
    && apt-get -y install python-pip

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install --disable-pip-version-check -r /requirements.txt

COPY ./src ./src/


# Use slim image to run the app.
FROM gcr.io/distroless/python3 AS runner
COPY --from=builder $VIRTUAL_ENV /venv
COPY --from=builder ./src /app

CMD [ "./app/hello-world.py"]