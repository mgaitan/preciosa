# -*- coding: utf-8 -*-
u"""
convierte el gejson de sucursales de supermercado de Open Street Map,
utilizando el servicio overpass-turbo.eu

el argumento es el un path o url al dump gjson,

Genera un archivo CSV en /datasets/sucursales/osm-<FECHA>.csv
con los resultados a partir de un dump gejson de la consulta
incluyendo cabeceras.
"""

# obtener el GeoJSON
# http://overpass-turbo.eu/?Q=node%0A%20%20[%22shop%22~%22supermarket%22]%0A%20%20%28area%3A3600286393%29%3B%0A%20%20out%20body%3B&C=-35.42487;-59.32617;4   # NOQA

import os
import urllib2
import logging
import unicodecsv
from datetime import datetime
import json
from django.core.management.base import BaseCommand, CommandError
from tools.gis import donde_queda
from tools.sucursales import inferir_cadena

try:
    from progress.bar import Bar
except ImportError:
    print """Instalaste las dependecias extra?:
        $ pip install -r requirements/extra.txt  """
    raise

from django.conf import settings

from preciosa.datos.adaptors import SUCURSAL_COLS


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<file_geojson>'
    help = __doc__

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError(
                'dame el geojson, pa'
            )

        geojson = args[0]
        if geojson.startswith('http'):
            fh = urllib2.urlopen(geojson)
        else:
            fh = open(args[0])
        data = json.load(fh)

        suc_dir = os.path.join(settings.DATASETS_ROOT, 'sucursales')
        if not os.path.exists(suc_dir):
            os.makedirs(suc_dir)

        FILENAME = 'osm_%s.csv' % datetime.now().strftime("%Y-%m-%d-%H%M%S")
        FILENAME = os.path.join(suc_dir, FILENAME)
        writer = unicodecsv.DictWriter(open(FILENAME, 'wb'), SUCURSAL_COLS)
        writer.writeheader()
        bar = Bar('Convirtiendo ', suffix='%(percent)d%%')
        for feature in bar.iter(data['features']):
            sucursal = self.parse_sucursal(feature)
            writer.writerow(sucursal)

    def parse_sucursal(self, feature):
        sucursal = {}
        sucursal['lon'], sucursal['lat'] = feature['geometry']['coordinates']
        sucursal.update(donde_queda(sucursal['lat'], sucursal['lon']))
        props = feature['properties']
        sucursal['nombre'] = props['name']
        sucursal['telefono'] = props.get('phone', None)
        sucursal['url'] = props.get('website', None)
        cadena = inferir_cadena(sucursal['nombre'])
        if cadena:
            sucursal['cadena_id'] = cadena[1]
        return sucursal
