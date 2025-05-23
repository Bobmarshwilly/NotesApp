FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -LsS https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN python -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv sync && \
    pip install --no-cache-dir -e . && \
    alembic --version

COPY . .

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.notes_app.__main__:app --host 0.0.0.0 --port 8000"]