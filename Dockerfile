FROM python:3.9-slim

RUN mkdir /app

WORKDIR /app

COPY pyproject.toml .

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

ENTRYPOINT ["sh", "./entrypoint.sh"]