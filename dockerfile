FROM python:3.12-slim

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev python3-dev \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
COPY alembic alembic.ini ./
COPY ./src ./src
COPY ./docker-setting-up.sh .

RUN chmod +x docker-setting-up.sh

ENTRYPOINT [ "./docker-setting-up.sh" ]

EXPOSE 8000

CMD ["sh", "-c", "/app/.venv/bin/alembic upgrade head && /app/.venv/bin/uv run src/notes_app/__main__.py"]