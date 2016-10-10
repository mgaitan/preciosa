#!/bin/bash
python manage.py migrate
python manage.py loaddata \
	  fixtures/sites.json \
      fixtures/admin_dev.json \
      fixtures/flatpages.json \
      fixtures/blog.json \
      fixtures/ciudades.json \
      fixtures/sucursales.json \
      fixtures/categorias.json \
      fixtures/marcas.json \
      fixtures/productos.json \
      fixtures/precios.json

