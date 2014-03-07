# -*- coding: utf-8 -*-
from django.test import TestCase
from preciosa.precios.models import Producto
from preciosa.precios.tests.factories import ProductoFactory, CategoriaFactory


# taken from https://github.com/jazzido/producto-similaridades
PRODUCTOS = u"""Milanesas de soja MONDO FRIZZATTA ceb/que cja 380 grm
Milanesa de soja jamon & queso mf 380gr
Milanesa de soja jamon y queso swift 380gr
Milanesas de soja finca natural 340 gr
Mondo Frizzatta - Cebolla y Queso Milanesa de soja rellenas con cebolla y queso. Congelado. 4 unidades. 380 Grs
Mondo Frizzatta - Choclo y Queso Milanesa de soja rellenas con choclo y queso. Congelado. 4 unidades. 380 Grs
Mondo Frizzatta - Jamón y Queso Milanesa de soja rellenas con jamón y queso. Congelado. 4 unidades. 380 Grs
Mondo Frizzatta - Tomate y Queso Milanesa de soja rellenas con tomate y queso. Congelado. 4 unidades. 380 Grs
Mondo Frizzatta - Espinaca y Queso Milanesa de soja rellenas con espinaca y queso. Congelado. 4 unidades. 380 Grs
Milanesa de soja espinaca & queso mf 380gr
Mondo Frizzatta - Medallones de merluza Congelado. 300 Grs
Cloro shock clorotec 4kg
Cloro shock clorotec 1kg
Cloro fresclor shock 1 kg
Cloro granulado clorotec 1 kg
un producto que nada que ver""".split('\n')


class TestProductoSimilarity(TestCase):

    def setUp(self):
        cat = CategoriaFactory()
        self.productos = [ProductoFactory(descripcion=d,
                                          categoria=cat) for d in PRODUCTOS]
        self.q = 'Milanesas de soja MONDO FRIZZATTA ceb/que cja 380 grm'
        self.qs = self.f(self.q)

    def f(self, q=None):
        return Producto.objects.filter_o(descripcion__similar=q or self.q)

    def test_primer_resultado_es_el_textual(self):
        self.assertEqual(self.qs[0].descripcion, self.q)
        self.assertEqual(self.qs[0].descripcion_distance, 1.0)

    def test_ordenado_por_distancia(self):
        result = [p.descripcion_distance for p in self.qs]
        self.assertEqual(sorted(result, reverse=True), result)

    def test_solo_resultados_relevantes(self):
        nada_que_ver = Producto.objects.get(descripcion='un producto que nada que ver')
        self.assertFalse(self.qs.filter(id=nada_que_ver.id).exists())
        self.assertFalse(self.qs.filter(descripcion__contains='Cloro').exists())

    def test_distancias(self):
        p1 = self.qs.get(descripcion="Mondo Frizzatta - Cebolla y Queso Milanesa de soja "
                                "rellenas con cebolla y queso. Congelado. 4 unidades. "
                                "380 Grs")
        p2 = self.qs.get(descripcion="Mondo Frizzatta - Choclo y Queso Milanesa de soja "
                                     "rellenas con choclo y queso. Congelado. 4 unidades. "
                                     "380 Grs")
        self.assertGreater(p1.descripcion_distance, p2.descripcion_distance)

    def test_de_la_milanga(self):
        # esto deberia hacer explotar el equipo que hace el request
        # por hereje. La "milanga" es de carne!
        qs = self.f("milanga de soja")
        self.assertTrue(qs.exists())

    def test_cloro(self):
        qs = self.f("cloro")
        self.assertEqual(qs.count(), 2)

