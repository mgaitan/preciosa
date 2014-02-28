from django.test import TestCase
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from preciosa.precios.models import Precio
from preciosa.precios.tests.factories import (SucursalFactory,
                                              ProductoFactory,
                                              PrecioFactory)


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
        self.assertEqual(list(self.qs()), [{'precio': Decimal('10.56'),
                                            'created': p.created}])

    def test_precio_mas_nuevo_primero(self):
        p = self.add('10.56')
        p2 = self.add('11.20')      # mas nuevo
        self.assertEqual(list(self.qs()),
                         [{'precio': Decimal('11.20'),
                           'created': p2.created},
                          {'precio': Decimal('10.56'),
                           'created': p.created}])

    def test_mismo_precio_queda_solo_el_mas_nuevo(self):
        p = self.add('10.56')
        p2 = self.add('11.20')
        p3 = self.add('11.20')      # noqa
        p4 = self.add('11.30')
        self.assertEqual(list(self.qs()),
                         [{'precio': Decimal('11.30'),
                           'created': p4.created},
                          {'precio': Decimal('11.20'),
                           'created': p2.created},
                          {'precio': Decimal('10.56'),
                           'created': p.created}])

    def test_mas_nuevos_que(self):
        limite = timezone.now() - timedelta(10)
        # registro de hace 10 dias
        p = self.add('10.56', created=limite)
        # registro de hoy
        p2 = self.add('11.20')
        self.assertEqual(list(self.qs()),
                         [{'precio': Decimal('11.20'),
                           'created': p2.created},
                          {'precio': Decimal('10.56'),
                           'created': p.created}])
        self.assertEqual(list(self.qs(dias=11)),
                         [{'precio': Decimal('11.20'),
                           'created': p2.created},
                          {'precio': Decimal('10.56'),
                           'created': p.created}])
        # caso limite. seria mejor usar __range  ?
        self.assertEqual(list(self.qs(dias=10)),
                         [{'precio': Decimal('11.20'),
                           'created': p2.created}])
        self.assertEqual(list(self.qs(dias=9)),
                         [{'precio': Decimal('11.20'),
                           'created': p2.created}])

    def test_historial_completo(self):
        p = self.add('10.56')
        p2 = self.add('11.20')
        p3 = self.add('11.20')      # noqa
        p4 = self.add('11.30')
        self.assertEqual(list(self.qs(distintos=False)),
                         [{'precio': Decimal('11.30'),
                           'created': p4.created},
                          {'precio': Decimal('11.20'),
                           'created': p3.created},
                          {'precio': Decimal('11.20'),
                           'created': p2.created},
                          {'precio': Decimal('10.56'),
                           'created': p.created}])


class TestMasProbables(TestCase):

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

    def qs(self, **kwargs):
        return Precio.objects.mas_probables(sucursal=self.suc,
                                            producto=self.producto,
                                            **kwargs)

    def test_si_hay_precios_de_la_sucursal_devuelve_esos(self):
        p1 = self.add(10, sucursal=self.suc)
        p2 = self.add(20, sucursal=self.suc)
        self.assertEqual(list(self.qs()),
                         [{'precio': Decimal('20'),
                           'created': p2.created},
                          {'precio': Decimal('10'),
                           'created': p1.created}])

    def test_precios_misma_cadena_en_la_ciudad(self):
        p1 = self.add(10, sucursal=self.suc2)
        p2 = self.add(11, sucursal=self.suc3)
        self.assertEqual(list(self.qs()),
                         [{'precio': Decimal('11'),
                           'created': p2.created},
                          {'precio': Decimal('10'),
                           'created': p1.created}])


