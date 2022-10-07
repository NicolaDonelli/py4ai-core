# syntax=docker/dockerfile:1

FROM python:3.7-slim-buster as builder

WORKDIR /app

COPY requirements/requirements.in requirements/requirements.in
COPY requirements/requirements_dev.txt requirements/requirements_dev.txt
COPY LICENSE MANIFEST.in versioneer.py setup.py setup.cfg README.md ./
COPY py4ai py4ai
COPY tests tests
RUN pip install -r requirements/requirements_dev.txt
RUN python3 -m pytest
RUN python3 setup.py sdist

FROM python:3.7-slim-buster
WORKDIR /app
COPY --from=builder /app/dist /app/dist
RUN ls -t ./dist/*.tar.gz | xargs pip install
ENTRYPOINT ["python"]
