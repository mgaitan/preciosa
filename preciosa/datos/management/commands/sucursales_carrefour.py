# -*- coding: utf-8 -*-
u"""
script basico para scrapping de sucursales de datos Carrefour

Genera un archivo CSV en /datasets/sucursales/carrefour.csv
con los resultados, incluyendo cabeceras.
"""
import os
import logging
import unicodecsv
from datetime import datetime

import requests
from django.core.management.base import BaseCommand
from pyquery import PyQuery
from tools.sucursales import inferir_ciudad, PROVINCIAS
from cities_light.models import City
try:
    from progress.bar import Bar
except ImportError:
    print """Instalaste las dependecias extra?:
        $ pip install -r requirements/extra.txt  """
    raise
from tools import texto
from django.conf import settings

from preciosa.datos.adaptors import SUCURSAL_COLS


logger = logging.getLogger(__name__)

DESDE = 3990   # poblacion minima de ciudad donde buscar supermercados


CARREFOUR_ID = 7
EXPRESS_ID = 12
MARKET_ID = 13
MAXI_ID = 17

nombre2id = {'Carrefour hiper': CARREFOUR_ID,
             'Carrefour express': EXPRESS_ID,
             'Carrefour market': MARKET_ID,
             'Carrefour maxi': MAXI_ID}


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):

        def parse_buscador(r):
            pq = PyQuery(r.content)
            return pq('div.storelocator_result')

        suc_dir = os.path.join(settings.DATASETS_ROOT, 'sucursales')
        if not os.path.exists(suc_dir):
            os.makedirs(suc_dir)

        FILENAME = 'carrefour_%s.csv' % datetime.now().strftime("%Y-%m-%d-%H%M%S")
        FILENAME = os.path.join(suc_dir, FILENAME)

        writer = unicodecsv.DictWriter(open(FILENAME, 'wb'), SUCURSAL_COLS)
        writer.writeheader()

        ciudades = City.objects.filter(country__name='Argentina',
                                       population__gt=DESDE)
        results = []

        bar = Bar('Obteniendo sucursales de Carrefour', suffix='%(percent)d%%')
        for city in bar.iter(ciudades):
            r = requests.post('http://www.carrefour.com.ar/storelocator/index/search/',
                              {'search[address]': 'Mendoza, Argentina',
                               'search[geocode]': '%s, %s' % (city.latitude,
                                                              city.longitude)})
            results.extend(parse_buscador(r))

        # html = '\n\n'.join(PyQuery(r).html() for r in results)
        # f = open(FILENAME + '.html', 'w')
        # f.write(html.encode('utf8'))

        CONOCIDOS = []
        nuevas = 0
        bar = Bar('Extrayendo información de nuevas sucursales', suffix='%(percent)d%%')
        for suc in bar.iter(results):
            supermercado = self.parse_suc(suc)
            nombre = supermercado['nombre']
            if nombre in CONOCIDOS:
                # print("%s ya cargado" % nombre)
                continue
            CONOCIDOS.append(nombre)
            # print(supermercado)
            writer.writerow(supermercado)
            nuevas += 1

        print "Se encontraron %d sucursales únicas de Carrefour (%d resultados)" % (nuevas,
                                                                                    len(ciudades))

    def parse_suc(self, html_snippet):
        pq = PyQuery(html_snippet)
        data = {}
        data['nombre'] = 'Sucursal ' + pq('.name a').text()
        data['cadena_nombre'] = pq('.name + div img').attr('title')
        data['cadena_id'] = nombre2id[data['cadena_nombre']]
        data['direccion'] = pq('.name + div + div').text()

        prov_ciudad = pq('.name + div + div + div').text()
        normal_prov_ciudad = texto.normalizar(prov_ciudad)
        prov_ciudad = prov_ciudad.split()
        for p in PROVINCIAS:
            if p in normal_prov_ciudad:
                break
        else:
            assert ValueError("provincia en %s" % normal_prov_ciudad)

        # la pampa, la rioja
        sep = len(p.split())
        data['provincia'] = " ".join(prov_ciudad[:sep])
        data['ciudad'] = " ".join(prov_ciudad[sep:])

        ciudad = inferir_ciudad(data['ciudad'], data['provincia'])
        if ciudad:
            data['ciudad_relacionada_id'] = ciudad[2]
        ubicacion = pq('.encuentra-la-ruta').attr('rel').split('l(')[1][:-1].split(', ')
        data['lat'], data['lon'] = ubicacion
        data['telefono'] = pq('.name + div + div + div + div').text().strip()
        return data