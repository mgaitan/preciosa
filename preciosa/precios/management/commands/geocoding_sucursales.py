# -*- coding: utf-8 -*-

import requests

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError

from preciosa.precios.models import Sucursal

geocoding_url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false'

class Command(BaseCommand):
    help = 'GeoCoding para ubicar Sucursales en base a su domicilio.'

    def handle(self, *args, **options):
        for sucursal in Sucursal.objects.filter(ubicacion=None):
            address = u"%(direccion)s, %(ciudad)s" % {
                'direccion': sucursal.direccion,
                'ciudad': sucursal.ciudad.name
            }

            if sucursal.ciudad.region:
                address += u", %(region)s" % {
                    'region': sucursal.ciudad.region.name
                }

            address += u", %(pais)s" % {'pais': sucursal.ciudad.country.name}

            self.stdout.write(u'ID#%s "%s" -> "%s" ...' % (
                sucursal.id, sucursal.nombre, address
            ))

            res = requests.get(geocoding_url % address)
            json_data = res.json()

            if json_data['results']:
                self.stdout.write(u'  -> Encontrado!')

                # fr = first_result / first_row
                fr = json_data['results'][0]

                lat = fr['geometry']['location']['lat']
                lon = fr['geometry']['location']['lng']

                self.stdout.write(u'     + %s' % fr['formatted_address'])
                self.stdout.write(u'     + %s' % fr['geometry']['location'])

                sucursal.ubicacion = Point(lon, lat)
                sucursal.save()

            else:
                self.stdout.write(u'  -> No se encontró :(')


        self.stdout.write(u'Fin!')
