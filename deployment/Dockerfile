FROM python:3.10-slim

RUN apt-get update \
    && apt-get -qq install \
    gcc \
    && pip install --upgrade pip \
    && pip install \
      poetry==1.3.2 \
      "urllib3<2.0.0" \
    && poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /app/

WORKDIR /app

RUN --mount=type=ssh poetry install --no-root

RUN rm -rf /root/.cache \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq autoremove \
    && apt-get clean

COPY /bwg /app/bwg
COPY /config /app/config
COPY .env entrypoint.sh README.md /app

RUN --mount=type=ssh poetry install

ENV PYTHONUNBUFFERED 1

EXPOSE 8080
ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["sleep", "infinity"]
