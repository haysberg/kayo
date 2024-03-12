FROM python:3.12-slim as python-base

ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/app/venv

# Create stage for Poetry installation
FROM python-base as poetry-base

# Administrative tasks
RUN apt update -y && apt upgrade -y && apt autoremove -y && apt clean -y

RUN pip install --upgrade pip

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry

# Create a new stage from the base python image
FROM python-base as kayo

LABEL org.opencontainers.image.source=https://github.com/haysberg/kayo

WORKDIR /app

# Copy Poetry to app image
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

# Copy Application & dependencies
COPY poetry.lock pyproject.toml referential.json README.md main.py ./
COPY ./kayo ./kayo 

ENV SETUPTOOLS_USE_DISTUTILS=stdlib

# Validate config && install dependencies
RUN poetry check && poetry install --only main --no-interaction --no-cache && mkdir data
ENV PYTHONUNBUFFERED=1

CMD [ "poetry", "run", "python", "main.py" ]
