FROM ubuntu:16.04

ENV PYTHONUNBUFFERED 1

RUN apt-get -qq update && apt-get install -y  --no-install-recommends \
    build-essential \
    git \
    postgresql-client \
    python \
    python-dev \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng12-dev \
    binutils \
    libproj-dev \
    gdal-bin \
    python-pip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code

ADD . /code/
RUN pip install -U pip setuptools
RUN pip install -r requirements.txt
