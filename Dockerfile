FROM ubuntu:16.04

ENV PYTHONUNBUFFERED 1

RUN apt-get -qq update && apt-get install -y  --no-install-recommends \
    build-essential \
    python \
    python-dev \
    libffi-dev libssl-dev \
    libpq-dev \
    libxml2-dev libxslt1-dev \
    libjpeg-dev zlib1g-dev libpng12-dev \
    gdal-bin \
    python-pip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code

ADD . /code/
RUN pip install -U pip setuptools
RUN pip install -r requirements.txt

RUN python manage.py createsuperuser --username=admin
RUN python manage.py loaddata fixtures/flatpages.json \
    fixtures/blog.json fixtures/newsletter.json \
    fixtures/ciudades.json fixtures/sucursales.json \
    fixtures/categorias.json fixtures/marcas.json \
    fixtures/productos.json fixtures/precios.json

