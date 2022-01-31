FROM python:3.9-slim

RUN mkdir /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN python3 manage.py collectstatic --no-input
