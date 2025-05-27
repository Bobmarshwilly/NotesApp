#!/bin/sh
set -e

python -m venv /app/.venv

/app/.venv/bin/pip install uv
/app/.venv/bin/uv sync
/app/.venv/bin/pip install --no-cache-dir -e /app

exec "$@"