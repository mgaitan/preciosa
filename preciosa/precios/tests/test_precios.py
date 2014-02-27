from django.test import TestCase
from decimal import Decimal
from preciosa.precios.models import Precio
from preciosa.precios.tests.factories import (SucursalFactory,
                                              ProductoFactory,
                                              PrecioFactory)


class TestPrecioHistorico(TestCase):

    def setUp(self):
        self.sucursal = SucursalFactory()
        self.producto = ProductoFactory()

    def qs(self):
        return Precio.objects.historico(sucursal=self.sucursal,
                                        producto=self.producto)

    def add(self, precio):
        return PrecioFactory(sucursal=self.sucursal,
                             producto=self.producto,
                             precio=precio)

    def test_sin_precios(self):
        self.assertEqual(list(self.qs()), [])

    def test_unico(self):
        p = self.add('10.56')
        self.assertEqual(list(self.qs()), [{'precio': Decimal('10.56'),
                                            'created': p.created}])

    def test_precio_mas_nuevo_primero(self):
        p = self.add('10.56')
        p2 = self.add('11.20')
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
