#!/usr/bin/env bash
poetry run alembic revision --autogenerate
poetry run alembic upgrade head
exec "$@"