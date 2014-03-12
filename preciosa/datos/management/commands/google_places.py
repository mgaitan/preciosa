# -*- coding: utf-8 -*-
u"""
script basico para adquisición de datos de
sucursales de supermercados desde Google Places.

Genera un archivo CSV en /datasets/sucursales/google_places_<DATE>.csv
con los resultados, incluyendo cabeceras.
"""
import os
import logging
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
import unicodecsv

try:
    from googleplaces import GooglePlaces, types, lang
except ImportError:
    print """¿Instalaste las dependecias extra?:
    $ pip install -r requirements/extra.txt"""
    raise

from cities_light.models import City

logger = logging.getLogger(__name__)

DESDE = 6990   # poblacion minima de ciudad donde buscar supermercados


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        # setup del archivo de salida

        fieldnames = ['nombre',
                      'direccion',
                      'ciudad',
                      'provincia',
                      'lon',
                      'lat',
                      'ciudad_relacionada_id',
                      'telefono',
                      'url']

        suc_dir = os.path.join(settings.DATASETS_ROOT, 'sucursales')
        if not os.path.exists(suc_dir):
            os.makedirs(suc_dir)

        FILENAME = 'google_place_%s.csv' % datetime.now().strftime("%Y%m%d%H%M%S")
        FILENAME = os.path.join(suc_dir, FILENAME)

        writer = unicodecsv.DictWriter(open(FILENAME, 'wb'), fieldnames)
        writer.writeheader()

        # crear manager de la api
        google_places = GooglePlaces(settings.GOOGLE_PLACES_API_KEY)

        IDS_CONOCIDOS = []

        for ciudad in City.objects.filter(population__gte=DESDE).order_by('-population'):
            location = unicode(ciudad).encode('utf8')
            query_result = google_places.nearby_search(name='supermercado',
                                                       language=lang.SPANISH,
                                                       location=location,
                                                       types=[types.TYPE_GROCERY_OR_SUPERMARKET],  # NOQA
                                                       radius=2000)

            for place in query_result.places:
                if place.id in IDS_CONOCIDOS:
                    print("%s ya cargado" % place.name)
                    continue
                IDS_CONOCIDOS.append(place.id)
                supermercado = self.limpiar(place, ciudad)
                print(supermercado)
                writer.writerow(supermercado)

    def limpiar(self, place, ciudad):
        """
        devuelve un diccionario con las siguientes claves::

            nombre, direccion, lon, lat, ciudad_segun_google,
            related_city_id, telefono, url
        """
        place.get_details()
        suc = {}

        # Place a veces no trae la direccion
        # y quedará (ciudad, provincia), en vez de (direccion, ciudad)
        # Se deberia hacer un reverse lookup a partir de la localizacion
        # via la API de google maps.
        dire = place.formatted_address.split(',')
        hay = len(dire) == 4
        suc['direccion'] = dire[0].strip() if hay else ''
        suc['ciudad'] = dire[1].strip() if hay else dire[0].strip()
        suc['provincia'] = dire[2].strip() if hay else dire[1].strip()
        suc['provincia'] = suc['provincia'].strip(' Province')
        suc['nombre'] = place.name
        suc['lon'] = place.geo_location['lng']
        suc['lat'] = place.geo_location['lat']
        suc['telefono'] = place.local_phone_number
        suc['url'] = place.website

        # como google place busca un radio a partir de una ciudad, no necesariamente
        # el supermercado encontrados **es** de la ciudad.
        # La ciudad_relacionada debe tomarse sólo como referencia.
        # lo mejor seria "normalizar" `ciudad` a la instancia
        # correcta.
        suc['ciudad_relacionada_id'] = ciudad.id
        return suc
