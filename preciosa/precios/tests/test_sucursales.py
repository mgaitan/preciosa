# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.exceptions import ValidationError
from preciosa.precios.tests.factories import (SucursalFactory,
                                              CadenaFactory,
                                              CityFactory)
from tools.gis import punto_destino
from tools import texto

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
        otra_ubicacion = punto_destino(suc.ubicacion, 90, 0.03)
        with self.assertRaisesRegexp(ValidationError, 'sucursal(.*)metros'):
            suc2 = SucursalFactory(ubicacion=otra_ubicacion, cadena=suc.cadena)
            suc2.clean()

    def test_si_no_tiene_ubicacion_no_se_verifica_el_radio(self):
        suc = SucursalFactory(ubicacion=None)
        suc2 = SucursalFactory(cadena=suc.cadena)
        self.assertIsNone(suc2.clean())

    def test_sucursales_mas_de_50_no_afectan(self):
        suc = SucursalFactory()
        otra_ubicacion = punto_destino(suc.ubicacion, 90, 0.06)
        suc2 = SucursalFactory(ubicacion=otra_ubicacion, cadena=suc.cadena)
        self.assertIsNone(suc2.clean())

    def test_sucursales_otra_cadena_no_afectan_en_radio(self):
        suc = SucursalFactory()
        otra_ubicacion = punto_destino(suc.ubicacion, 90, 0.03)
        suc2 = SucursalFactory(ubicacion=otra_ubicacion)
        assert suc2.cadena != suc.cadena
        self.assertIsNone(suc2.clean())


class TestSucursalCercanas(TestCase):

    def setUp(self):
        self.suc = SucursalFactory()

    def test_radio(self):
        suc2 = SucursalFactory(ubicacion=punto_destino(self.suc.ubicacion, 90, 0.1))
        suc3 = SucursalFactory(ubicacion=punto_destino(self.suc.ubicacion, 90, 1))
        suc4 = SucursalFactory(ubicacion=punto_destino(self.suc.ubicacion, 180, 1.2))
        cercanas = self.suc.cercanas(radio=1.1)
        self.assertIn(suc2, cercanas)
        self.assertIn(suc3, cercanas)
        self.assertNotIn(self.suc, cercanas)
        self.assertNotIn(suc4, cercanas)

    def test_misma_cadena(self):
        suc2 = SucursalFactory(ubicacion=punto_destino(self.suc.ubicacion, 90, 0.1),
                               cadena=self.suc.cadena)
        suc3 = SucursalFactory(ubicacion=punto_destino(self.suc.ubicacion, 90, 1))
        cercanas = self.suc.cercanas(radio=2, misma_cadena=True)
        self.assertIn(suc2, cercanas)
        self.assertNotIn(suc3, cercanas)
        self.assertNotIn(self.suc, cercanas)


class TestSucursalBusqueda(TestCase):

    def test_incluye_direccion(self):
        calle = u'Av San Martín'
        self.suc = SucursalFactory(direccion=calle)

        self.assertIn(texto.normalizar(calle), self.suc.busqueda)

    def test_incluye_nombre(self):
        self.suc = SucursalFactory(nombre=u'Sucursal Plaza Once')
        self.assertIn('plaza once', self.suc.busqueda)
        # no incluye palabras demasiado comunes
        self.assertNotIn('sucursal', self.suc.busqueda)

    def test_incluye_nombre_cadena(self):
        cadena = CadenaFactory(nombre='Jumbo')
        self.suc = SucursalFactory(cadena=cadena)
        self.assertIn('jumbo', self.suc.busqueda)

    def test_incluye_ciudad(self):
        ciudad = CityFactory(name='La Cumbre')
        self.suc = SucursalFactory(ciudad=ciudad)
        self.assertIn('la cumbre', self.suc.busqueda)

    def test_incluye_provincia_nombre(self):
        ciudad = CityFactory(name=u'Malargüe', region__name=u'Mendoza')
        self.suc = SucursalFactory(ciudad=ciudad)
        self.assertIn('malargue', self.suc.busqueda)
        self.assertIn('mendoza', self.suc.busqueda)





