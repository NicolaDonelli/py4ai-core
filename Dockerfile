# syntax=docker/dockerfile:1

ARG  PY_VERSION=3.7
FROM python:${PY_VERSION}-buster

WORKDIR /py4ai-core

RUN apt-get update && apt-get upgrade -y

COPY requirements/requirements.in requirements/requirements.in
COPY requirements/requirements_dev.in requirements/requirements_dev.in
COPY LICENSE MANIFEST.in versioneer.py setup.py pyproject.toml README.md Makefile ./
COPY .git .git
COPY py4ai py4ai
COPY tests tests

RUN addgroup --system tester && adduser --system --group tester
RUN chown -R tester:tester /py4ai-core

# change to the tester user: switch to a non-root user is a best practice.
USER tester
ENV PATH ${PATH}:/home/tester/.local/bin

CMD make checks