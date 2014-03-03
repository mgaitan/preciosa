# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.exceptions import ValidationError
from preciosa.precios.tests.factories import (SucursalFactory,)
from tools.gis import punto_destino


class TestSucursalClean(TestCase):

    def setUp(self):
        pass

    def test_al_menos_cadena_o_nombre_sucursal(self):
        with self.assertRaisesRegexp(ValidationError, 'cadena o el nombre'):
            suc = SucursalFactory(cadena=None, nombre='')
            suc.clean()

    def test_online_o_fisica(self):
        with self.assertRaisesRegexp(ValidationError, 'online'):
            suc = SucursalFactory(online=True, direccion=u'Durazno y Convención')
            suc.clean()

    def test_online_necesita_url(self):
        with self.assertRaisesRegexp(ValidationError, 'url es obligatoria'):
            suc = SucursalFactory(online=True, url=None)
            suc.clean()

    def test_fisica_necesita_direccion(self):
        with self.assertRaisesRegexp(ValidationError, u'sica(.*)dire'):
            suc = SucursalFactory(online=False, direccion=None)
            suc.clean()

    def test_ya_existe_en_radio_de_la_misma_cadena(self):
        suc = SucursalFactory()
        otra_ubicacion = punto_destino(suc.point, 90, 0.03)
        with self.assertRaisesRegexp(ValidationError, 'sucursal(.*)metros'):
            suc2 = SucursalFactory(ubicacion=otra_ubicacion, cadena=suc.cadena)
            suc2.clean()

    def test_si_no_tiene_ubicacion_no_se_verifica_el_radio(self):
        suc = SucursalFactory(ubicacion=None)
        suc2 = SucursalFactory(cadena=suc.cadena)
        self.assertIsNone(suc2.clean())

    def test_sucursales_mas_de_50_no_afectan(self):
        suc = SucursalFactory()
        otra_ubicacion = punto_destino(suc.point, 90, 0.06)
        suc2 = SucursalFactory(ubicacion=otra_ubicacion, cadena=suc.cadena)
        self.assertIsNone(suc2.clean())

    def test_sucursales_otra_cadena_no_afectan_en_radio(self):
        suc = SucursalFactory()
        otra_ubicacion = punto_destino(suc.point, 90, 0.03)
        suc2 = SucursalFactory(ubicacion=otra_ubicacion)
        assert suc2.cadena != suc.cadena
        self.assertIsNone(suc2.clean())


