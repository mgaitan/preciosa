"""
utilidades relacionadas a GIS
"""

import requests


GEOCODING_URL = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false'


def get_geocode_data(ciudad=None, direccion=None):
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