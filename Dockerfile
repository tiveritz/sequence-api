# Base Image
FROM python:3.9.7-alpine

# Work Directory
WORKDIR /usr/src

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# General
RUN apk update

# Postgres Client
RUN apk add --update --no-cache postgresql-client

# Postgres Dependencies
RUN apk add --update --no-cache --virtual .tmp-build-deps \
	gcc libc-dev linux-headers postgresql-dev

# Pillow Dependencies
RUN apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add jpeg-dev zlib-dev libjpeg \
    && apk del build-deps \
    # For cryptography
    && apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo

# Dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# Networking
EXPOSE 8000

CMD gunicorn --bind :8000 --workers 3 howtosapi.wsgi:application