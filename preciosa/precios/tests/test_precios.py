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
                                            'created': p.created }])
