# -*- coding: utf-8 -*-
from django.test import TestCase
from functools import partial
from mock import patch
from tools.gis import donde_queda
from preciosa.precios.tests.factories import CityFactory, SucursalFactory
from tools.gis import punto_destino

def mock_reverse_geocode(lat, lon, formatted=True,
                         barrio=u'La Boca',
                         ciudad=u'Federación',
                         calle=u'Avenida Entre Ríos',
                         altura=u'201-299'):
    return [{u'long_name': altura,
            u'short_name': altura,
            u'types': [u'street_number']},
           {u'long_name': calle,
            u'short_name': calle,
            u'types': [u'route']},
           {u'long_name': barrio,
            u'short_name': barrio,
            u'types': [u'neighborhood', u'political']},
           {u'long_name': ciudad,
            u'short_name': ciudad,
            u'types': [u'locality', u'political']},
           {u'long_name': ciudad,
            u'short_name': ciudad,
            u'types': [u'administrative_area_level_2', u'political']},
           {u'long_name': u'Entre Rios',
            u'short_name': u'ER',
            u'types': [u'administrative_area_level_1', u'political']},
           {u'long_name': u'Argentina',
            u'short_name': u'AR',
            u'types': [u'country', u'political']}]


class TestDondeQueda(TestCase):

    def setUp(self):
        self.patcher = patch('tools.gis.reverse_geocode')
        self.mock = self.patcher.start()

    def config(self, **kwargs):
        self.mock.side_effect = partial(mock_reverse_geocode, **kwargs)
        self.addCleanup(lambda p: p.stop(), self.patcher)

    def test_devuelve_direccion(self):
        self.config(calle='zaraza', altura='10')
        r = donde_queda(-32, 1)
        self.assertEqual(r['direccion'], 'zaraza 10')

    def test_nombre_de_barrio(self):
        barrio = 'Villa Crespo'
        ciudad = CityFactory(name=barrio)
        self.config(barrio=barrio)
        r = donde_queda(-32, -46)
        self.assertEqual(r['ciudad'], ciudad)

    def test_nombre_de_Ciudad(self):
        ciudad = CityFactory(name=u'Neuquén')
        self.config(ciudad=u'Neuquén')
        r = donde_queda(-32, -46)
        self.assertEqual(r['ciudad'], ciudad)

    def test_detecta_ciudad_por_sucursal_cercana(self):
        suc = SucursalFactory()
        self.config()
        # está a 1 km
        punto = punto_destino(suc.ubicacion, 90, 1)
        r = donde_queda(punto.y, punto.x)
        self.assertEqual(r['ciudad'], suc.ciudad)
