FROM debian:11-slim AS build
ARG POETRY_VERSION=1.1.13
RUN apt-get update && \
  apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  python3 -m venv /venv && \
  /venv/bin/pip install --upgrade pip setuptools wheel && \
  /venv/bin/pip install "poetry==${POETRY_VERSION}"

FROM build AS build-venv
COPY pyproject.toml poetry.lock /
RUN /venv/bin/poetry export --without-hashes --format requirements.txt --output /requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r /requirements.txt

FROM gcr.io/distroless/python3-debian11
COPY --from=build-venv /venv /venv
COPY . /app
WORKDIR /app
ENTRYPOINT ["/venv/bin/python3", "src/main.py"]