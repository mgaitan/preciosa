# -*- coding: utf-8 -*-
from django.test import TestCase
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from preciosa.precios.models import Precio
from preciosa.precios.tests.factories import (SucursalFactory,
                                              ProductoFactory,
                                              PrecioFactory)
from tools.gis import punto_destino


class TestPrecioHistorico(TestCase):

    def setUp(self):
        self.sucursal = SucursalFactory()
        self.producto = ProductoFactory()

    def qs(self, **kwargs):
        return Precio.objects.historico(sucursal=self.sucursal,
                                        producto=self.producto,
                                        **kwargs)

    def add(self, precio, **kwargs):
        return PrecioFactory(sucursal=self.sucursal,
                             producto=self.producto,
                             precio=precio,
                             **kwargs)

    def test_sin_precios(self):
        self.assertEqual(list(self.qs()), [])

    def test_unico(self):
        p = self.add('10.56')
        self.assertEqual(list(self.qs()), [p])

    def test_precio_mas_nuevo_primero(self):
        p = self.add('10.56')
        p2 = self.add('11.20')      # mas nuevo
        self.assertEqual(list(self.qs()), [p2, p])

    def test_mismo_precio_queda_solo_el_mas_nuevo(self):
        p = self.add('10.56')
        p2 = self.add('11.20')
        p3 = self.add('11.20')      # noqa
        p4 = self.add('11.30')
        self.assertEqual(list(self.qs()),
                         [p4, p2, p])
        # FIX .este test no está bien. deberia ser
        # [p4, p3, p]  porque p3.created > p2.created  (más nuevo)

    def test_mas_nuevos_que(self):
        limite = timezone.now() - timedelta(10)
        # registro de hace 10 dias
        p = self.add('10.56', created=limite)
        # registro de hoy
        p2 = self.add('11.20')
        self.assertEqual(list(self.qs()), [p2, p])
        self.assertEqual(list(self.qs(dias=11)), [p2, p])
        # caso limite. seria mejor usar __range  ?
        self.assertEqual(list(self.qs(dias=10)), [p2])
        self.assertEqual(list(self.qs(dias=9)), [p2])

    def test_historial_completo(self):
        p = self.add('10.56')
        p2 = self.add('11.20')
        p3 = self.add('11.20')      # noqa
        p4 = self.add('11.30')
        self.assertEqual(list(self.qs(distintos=False)),
                         [p4, p3, p2, p])


class BaseTestPrecio(TestCase):

    def setUp(self):
        self.producto = ProductoFactory()
        self.suc = SucursalFactory()
        self.suc2 = SucursalFactory(ciudad=self.suc.ciudad,
                                    cadena=self.suc.cadena)
        self.suc3 = SucursalFactory(ciudad=self.suc.ciudad,
                                    cadena=self.suc.cadena)

    def add(self, precio=10, sucursal=None, **kwargs):
        if sucursal is None:
            sucursal = self.suc2

        return PrecioFactory(sucursal=sucursal,
                             producto=self.producto,
                             precio=precio,
                             **kwargs)


class TestMasProbables(BaseTestPrecio):

    def qs(self, **kwargs):
        return Precio.objects.mas_probables(sucursal=self.suc,
                                            producto=self.producto,
                                            **kwargs)

    def test_si_hay_precios_de_la_sucursal_devuelve_esos(self):
        p1 = self.add(10, sucursal=self.suc)
        p2 = self.add(20, sucursal=self.suc)
        self.assertEqual(list(self.qs()), [p2, p1])

    def test_precios_misma_cadena_en_la_ciudad(self):
        p1 = self.add(10, sucursal=self.suc2)
        p2 = self.add(11, sucursal=self.suc3)
        self.assertEqual(list(self.qs()), [p2, p1])

    def test_precios_a_radio_dado(self):
        self.suc2.ubicacion = punto_destino(self.suc.ubicacion, 90, 4.5)
        self.suc2.save()
        self.suc3.ubicacion = punto_destino(self.suc.ubicacion, 180, 4.7)
        self.suc3.save()
        p1 = self.add(10, sucursal=self.suc2)
        p2 = self.add(11, sucursal=self.suc3)
        # no hay sucursales dentro de este radio
        self.assertEqual(list(self.qs(radio=4.4)), [])
        # una sucursal dentro de este radio
        self.assertEqual(list(self.qs(radio=4.6)), [p1])
        # dos sucursales dentro de este radio
        self.assertEqual(list(self.qs(radio=4.8)), [p2, p1])

    def test_fallback_online(self):
        sucursal_online = SucursalFactory(cadena=self.suc.cadena,
                                          online=True,
                                          url='http://cadena.com')
        p1 = self.add(10, sucursal=sucursal_online)
        self.assertEqual(list(self.qs()), [p1])
        self.assertEqual(list(self.qs(radio=5)), [p1])


class TestMejoresPrecios(BaseTestPrecio):

    """
        # misma ciudad, distinta cadena
        self.suc4 = SucursalFactory(ciudad=self.suc.ciudad)
        # misma cadena, distinta ciudad
        self.suc5 = SucursalFactory(cadena=self.suc.cadena)
        # misma cadena, distinta ciudad
        self.suc5 = SucursalFactory(cadena=self.suc.cadena)
    """

    def qs(self, **kwargs):
        return Precio.objects.mejores(producto=self.producto,
                                              **kwargs)

    def test_precios_en_la_ciudad(self):
        self.add(precio=10, sucursal=self.suc)
        self.add(precio=11, sucursal=self.suc2)
        self.add(precio=8.4, sucursal=self.suc3)
        r = self.qs(ciudad=self.suc.ciudad)
        self.assertEqual(r[0].precio, Decimal('8.4'))
        self.assertEqual(r[0].sucursal, self.suc3)
        self.assertEqual(r[1].precio, Decimal('10'))
        self.assertEqual(r[1].sucursal, self.suc)
        self.assertEqual(r[2].precio, Decimal('11'))
        self.assertEqual(r[2].sucursal, self.suc2)

    def test_ciudad_o_radio_requerido(self):
        with self.assertRaisesRegexp(ValueError, 'ciudad o un radio'):
            self.qs()

    def test_punto_es_requerido_para_radio(self):
        with self.assertRaisesRegexp(ValueError, 'radio debe proveer el punto'):
            self.qs(radio=10)

    def test_precios_de_otra_ciudad_no_afectan(self):
        otra = SucursalFactory()
        assert self.suc.ciudad != otra.ciudad
        self.add(precio=10, sucursal=self.suc)
        self.add(precio=1, sucursal=otra)       # barato!
        r = self.qs(ciudad=self.suc.ciudad)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].precio, Decimal('10'))

    def test_precios_limite(self):
        # 3 precios posibles
        self.add(precio=10, sucursal=self.suc)
        self.add(precio=11, sucursal=self.suc2)
        self.add(precio=8.4, sucursal=self.suc3)
        r = self.qs(ciudad=self.suc.ciudad, limite=2)
        self.assertEqual(len(r), 2)

    def test_dias(self):
        limite = timezone.now() - timedelta(10)
        # registro de hace 10 dias
        self.add('9.20', sucursal=self.suc, created=limite)
        # registro de hoy
        p2 = self.add('10.56', sucursal=self.suc)
        r = self.qs(ciudad=self.suc.ciudad, dias=9)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], p2)

    def test_por_radio(self):
        self.suc2.ubicacion = punto_destino(self.suc.ubicacion, 90, 4.5)
        self.suc2.save()
        self.suc3.ubicacion = punto_destino(self.suc.ubicacion, 180, 4.7)
        self.suc3.save()
        p1 = self.add(precio=10, sucursal=self.suc)
        p2 = self.add(precio=8.4, sucursal=self.suc2)
        p3 = self.add(precio=11, sucursal=self.suc3)

        # por punto o ubicacion
        for p in (self.suc, self.suc.ubicacion):
            self.assertEqual(list(self.qs(radio=4.4, punto_o_sucursal=p)),
                             [p1])
            # una sucursal dentro de este radio
            self.assertEqual(list(self.qs(radio=4.6, punto_o_sucursal=p)),
                             [p2, p1])

            # dos sucursales dentro de este radio
            self.assertEqual(list(self.qs(radio=4.8, punto_o_sucursal=p)),
                             [p2, p1, p3])

    def test_solo_ultimo_precio_de_una_sucursal(self):
        p1 = self.add(precio=10, sucursal=self.suc)
        self.add(precio=11, sucursal=self.suc2)
        p3 = self.add(precio='9.5', sucursal=self.suc2)
        r = self.qs(ciudad=self.suc.ciudad)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], p3)
        self.assertEqual(r[1], p1)

    def test_vacio_si_no_hay_resultados(self):
        r = self.qs(ciudad=self.suc.ciudad)
        self.assertEqual(r, [])
