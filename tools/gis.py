# -*- coding: utf-8 -*-
"""
utilidades relacionadas a GIS
"""

import math
import requests
from django.contrib.gis.geos import Point


BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false'
GEOCODING_URL = BASE_URL + '&address=%s'
REVERSE_GEOCODING_URL = BASE_URL + '&latlng=%(lat)s,%(lon)s'


def geocode(ciudad=None, direccion=None):
    """
    usa google maps para obtener el
    GeoCoding para ubicar geolocalizamente una direccion

    Si direccion o ciudad se pasa, sobreescribe la direccion de la instancia
    """
    if not ciudad:
        return {}

    if not direccion:
        return {'lat': float(ciudad.latitude),
                'lon': float(ciudad.longitude),
                'direccion': unicode(ciudad)}

    q = u"%(direccion)s, %(ciudad)s" % {'direccion': direccion,
                                        'ciudad': ciudad.name}
    if ciudad.region:
        q += u", %(region)s" % {'region': ciudad.region.name}
    q += u", %(pais)s" % {'pais': ciudad.country.name}

    res = requests.get(GEOCODING_URL % q)
    json_data = res.json()
    if json_data['results']:
        fr = json_data['results'][0]
        lat = fr['geometry']['location']['lat']
        lon = fr['geometry']['location']['lng']
        return {'lat': lat, 'lon': lon,
                'direccion': fr['formatted_address']}
    return {}


def reverse_geocode(lat, lon):
    """usa google map para intentar devolver una
     dirección a partir de coordenada"""

    r = requests.get(REVERSE_GEOCODING_URL % locals()).json()
    if r['status'] != 'OK':
        return ''
    return r['results'][0]['formatted_address']


TIERRA_RADIO = 6371  # kilometros
TIERRA_ECUADOR = TIERRA_RADIO * 2 * math.pi  # circunferencia en el ecuador


def punto_destino(origen, angulo, distancia):
    """dado un punto `origen` encuentra un punto `destino`
       a un angulo y distancia dado

       código original por Angel "Java" López
       https://github.com/ajlopez/PythonSamples/blob/master/Tdd/geodistance/distancias.py
    """
    lon, lat = origen.x, origen.y
    radianes = math.radians(angulo)
    radio = math.fabs(math.cos(math.radians(lat))) * TIERRA_RADIO
    dest_latitud = lat + math.sin(radianes) * distancia / (TIERRA_ECUADOR / 360)
    dest_longitud = lon + math.cos(radianes) * distancia / (radio * 2 * math.pi / 360)
    return Point(dest_longitud, dest_latitud)
