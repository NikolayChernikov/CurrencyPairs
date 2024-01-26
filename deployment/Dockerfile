FROM python:3.10-slim

COPY poetry.lock pyproject.toml /app/

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install \
      poetry \
    && poetry config virtualenvs.create false
RUN --mount=type=ssh poetry install --no-root

RUN rm -rf /root/.cache \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq autoremove \
    && apt-get clean

COPY . /app
RUN --mount=type=ssh poetry install

ENV PYTHONUNBUFFERED 1

EXPOSE 8080
CMD ["sleep", "infinity"]
