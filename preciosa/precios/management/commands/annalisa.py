# -*- coding: utf-8 -*-

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from preciosa.precios.models import Sucursal


class Command(BaseCommand):
    help = 'Utiliza annalisa para inferir detalles a partir de la descripcion'

    def handle(self, *args, **options):
        for sucursal in Sucursal.objects.filter(ubicacion=None, online=False):
            self.stdout.write(u'%s' % sucursal)
            data = sucursal.get_geocode_data()
            if data:
                self.stdout.write(u'  -> Encontrado!')

                self.stdout.write(u'     + %s' % data['direccion'])
                self.stdout.write(u'     + Point(%s, %s)' % (data['lon'], data['lat']))

                sucursal.ubicacion = Point(data['lon'], data['lat'])
                sucursal.save()
            else:
                self.stdout.write(u'  -> No se encontró :(')


        self.stdout.write(u'Fin!')
