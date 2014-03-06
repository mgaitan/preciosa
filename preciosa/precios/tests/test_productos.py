# -*- coding: utf-8 -*-
from django.test import TestCase
from preciosa.precios.models import Producto
from preciosa.precios.tests.factories import ProductoFactory


# taken from https://github.com/jazzido/producto-similaridades
PRODUCTOS = """Milanesas de soja MONDO FRIZZATTA ceb/que cja 380 grm
Milanesa de soja jamon & queso mf 380gr
Milanesa de soja jamon y queso swift 380gr
Milanesas de soja finca natural 340 gr
Mondo Frizzatta - Cebolla y Queso Milanesa de soja rellenas con cebolla y queso. Congelado. 4 unidades. 380 Grs
Mondo Frizzatta - Choclo y Queso Milanesa de soja rellenas con choclo y queso. Congelado. 4 unidades. 380 Grs
Mondo Frizzatta - Jamón y Queso Milanesa de soja rellenas con jamó y queso. Congelado. 4 unidades. 380 Grs
Mondo Frizzatta - Tomate y Queso Milanesa de soja rellenas con tomate y queso. Congelado. 4 unidades. 380 Grs
Mondo Frizzatta - Espinaca y Queso Milanesa de soja rellenas con espinaca y queso. Congelado. 4 unidades. 380 Grs
Milanesa de soja espinaca & queso mf 380gr
Mondo Frizzatta - Medallones de merluza Congelado. 300 Grs""".split('\n')


class TestProductoSimilarity(TestCase):

    def setUp(self):
        self.productos = [ProductoFactory(descripcion=d) for d in PRODUCTOS]

    def qs(self, q):
        return Producto.objects.filter_o(descripcion__similar=q)

    def test_primer_resultado_es_el_textual(self):
        q = 'Milanesas de soja MONDO FRIZZATTA ceb/que cja 380 grm'
        qs = self.qs(q)
        self.assertEqual(qs[0].descripcion, q)
        self.assertEqual(qs[0].descripcion_distance, 1.0)
