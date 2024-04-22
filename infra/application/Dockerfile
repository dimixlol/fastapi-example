FROM python:3.11-alpine

ARG USER=python
ENV \
    PYTHONUNBUFFERED=1 \
    PIPEX_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_USE_SYSTEM=1

WORKDIR /app

RUN adduser -D -h /app -u 1000 "${USER}"

COPY --chown=${USER}:${USER} ./pyproject.toml /app/pyproject.toml
COPY --chown=${USER}:${USER} ./alembic.ini /app/alembic.ini
COPY --chown=${USER}:${USER} ./Pipfile /app/Pipfile
COPY --chown=${USER}:${USER} ./Pipfile.lock /app/Pipfile.lock

USER 0

RUN apk add postgresql-dev libffi-dev curl-dev openssl-dev make build-base \
    && pip install --upgrade pip setuptools pipenv==2023.6.12 \
    && pipenv sync --system

COPY --chown=${USER}:${USER} ./.env /app/.env
COPY --chown=${USER}:${USER} ./src /app/src
COPY --chown=${USER}:${USER} ./infra/application/entrypoint.sh /usr/local/bin/entrypoint.sh

USER 1000
ENTRYPOINT ["entrypoint.sh"]

CMD ["uvicorn", "src.application:app", "--host", "0.0.0.0", "--port", "8000"]
