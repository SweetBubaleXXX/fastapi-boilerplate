FROM python:3.11-alpine as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry~=1.7

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --with prod --without dev --no-root

FROM python:3.11-alpine

ENV PYTHONUNBUFFERED 1 \
    PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./deploy/gunicorn.conf.py ./alembic.ini ./

COPY ./src ./src

CMD [ "gunicorn", "-c", "gunicorn.conf.py", "src.main:create_app()" ]
