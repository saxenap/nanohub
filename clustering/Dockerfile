ARG py_version=3.8


# Use thick image to build.
FROM python:${py_version} AS python-image
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1
RUN set -xe \
    && apt-get -y update \
    && apt-get install -y --no-install-recommends \
    && apt-get install -y python3-pip
RUN pip install --upgrade pip --upgrade setuptools --upgrade wheel


FROM python-image AS pypackages-image
WORKDIR /build
RUN pip install pipenv
COPY ./Pipfile* /build/
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install


FROM python-image AS app-image
COPY . /app/


FROM python:${py_version}-slim-buster AS runner
WORKDIR /app
COPY --from=pypackages-image /build /app
COPY --from=app-image /app /app
ENTRYPOINT ["./.venv/bin/python3", "/app/hello-world.py"]


#FROM python AS app-dependencies
#
##COPY . .
##COPY Pipfile .
##RUN pip install pipenv
##RUN PIPENV_VENV_IN_PROJECT=1 pipenv install
##RUN pipenv lock --requirements > ./requirements.txt
##ENV PATH="/venv/bin:$PATH"
##RUN python3 -m venv /venv
#COPY ./src/* /app/
#COPY ./requirements.txt .
#RUN pip install -r requirements.txt
#
## Use slim image to run the app.
#FROM gcr.io/distroless/python3 AS runner
#
##COPY --from=app-dependencies /usr/local/lib/python3.8/site-packages/ /usr/lib/python3.8/.
##COPY ./src/ ./app
#COPY --from=app-dependencies ./app ./app
##COPY --from=app-dependencies /venv /venv
##ENV PYTHONPATH .
#ENV PYTHONPATH "${PYTHONPATH}:./app"
#ENTRYPOINT ["python3", "/app/hello-world.py"]
##CMD ["pipenv", "run", "python", "/app/hello-world.py"]


#ARG GIT_COMMIT_SHORT = sh(returnStdout: true, script:"git rev-parse --short=7 HEAD").trim()
#ARG GIT_COMMIT_SUBJECT = sh(returnStdout: true, script:"git log --format=%s -n 1 HEAD").trim()
#ARG GIT_COMMIT_AUTHOR = sh(returnStdout: true, script:"git log --format='%an' -n 1 HEAD").trim()
#ARG GIT_COMMIT_SUMMARY = "`<https://github.com/Kaggle/docker-python/commit/${GIT_COMMIT}|${GIT_COMMIT_SHORT}>` ${GIT_COMMIT_SUBJECT} - ${GIT_COMMIT_AUTHOR}"
#ARG SLACK_CHANNEL = sh(returnStdout: true, script: "if [[ \"${GIT_BRANCH}\" == \"master\" ]]; then echo \"#kernelops\"; else echo \"#builds\"; fi").trim()

#BUILD_ARGS+=" --build-arg GIT_COMMIT=$(git rev-parse HEAD)"
#BUILD_ARGS+=" --build-arg BUILD_DATE=$(date '+%Y%m%d-%H%M%S')"



#ARG GIT_COMMIT=unknown
#LABEL git-commit=$GIT_COMMIT
#
#ARG BUILD_DATE=unknown
#LABEL build-date=$BUILD_DATE
#
#RUN echo "$GIT_COMMIT" > /etc/git_commit && echo "$BUILD_DATE" > /etc/build_date