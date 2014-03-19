# -*- coding: utf-8 -*-
import os.path
from django.test import TestCase
from preciosa.precios.models import Sucursal
from preciosa.precios.tests.factories import CadenaFactory, CityFactory
from preciosa.datos.adaptors import SucursalCSVModel

DATASETS_PATH = os.path.join(os.path.dirname(__file__), 'datasets')


def _csv(filename):
    return os.path.join(DATASETS_PATH, filename)


class TestAdaptorSucursal(TestCase):

    def setUp(self):
        self.disco = CadenaFactory(id=6, nombre='Disco')
        self.jumbo = CadenaFactory(id=4, nombre='Jumbo')
        self.cba = CityFactory(id=4546, name=u'Córdoba')
        self.embalse = CityFactory(id=4118, name=u'Embalse')

    def test_importa_todas_las_que_tienen_direccion(self):
        assert Sucursal.objects.count() == 0
        sucursales, errors = SucursalCSVModel.import_data(data=_csv('sucursales.csv'))
        self.assertEqual(Sucursal.objects.count(), 2)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].line_number, 2)
        self.assertIn('debe tener dir', errors[0].error)

    def test_importa_bien(self):
        sucs, _ = SucursalCSVModel.import_data(data=_csv('sucursales.csv'))
        self.assertEqual(sucs[0], Sucursal.objects.all()[0])
        suc_disco = sucs[0]
        self.assertEqual(suc_disco.cadena, self.disco)
        self.assertEqual(suc_disco.direccion, 'Velez Sarsfield 1302')
        self.assertEqual(suc_disco.ciudad, self.cba)
        self.assertAlmostEqual(suc_disco.lon, -64.182231)
        self.assertAlmostEqual(suc_disco.lat, -31.413881)
        suc_cualca = sucs[1]
        self.assertIsNone(suc_cualca.cadena)
        self.assertEqual(suc_cualca.direccion, 'Gral Pistarini 260')
        self.assertEqual(suc_cualca.ciudad, self.embalse)
        self.assertAlmostEqual(suc_cualca.lon, -64.182129)
        self.assertAlmostEqual(suc_cualca.lat, -31.39893)




