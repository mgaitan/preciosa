# -*- coding: utf-8 -*-
import unittest
from django.test import TestCase
from django.db import IntegrityError
from preciosa.precios.models import Producto, DescripcionAlternativa
from preciosa.precios.tests.factories import ProductoFactory, CategoriaFactory
from tools.texto import normalizar

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


# class TestProductoSimilarity(TestCase):

#     def setUp(self):
#         cat = CategoriaFactory()
#         self.productos = [ProductoFactory(descripcion=d,
#                                           categoria=cat) for d in PRODUCTOS]
#         self.q = 'Milanesas de soja MONDO FRIZZATTA ceb/que cja 380 grm'
#         self.qs = self.f(self.q)

#     def f(self, q=None):
#         return Producto.objects.filter_o(descripcion__similar=q or self.q)

#     def test_primer_resultado_es_el_textual(self):
#         self.assertEqual(self.qs[0].descripcion, self.q)
#         self.assertEqual(self.qs[0].descripcion_distance, 1.0)

#     def test_ordenado_por_distancia(self):
#         result = [p.descripcion_distance for p in self.qs]
#         self.assertEqual(sorted(result, reverse=True), result)

#     def test_solo_resultados_relevantes(self):
#         nada_que_ver = Producto.objects.get(descripcion='un producto que nada que ver')
#         self.assertFalse(self.qs.filter(id=nada_que_ver.id).exists())
#         self.assertFalse(self.qs.filter(descripcion__contains='Cloro').exists())

#     def test_distancias(self):
#         p1 = self.qs.get(descripcion="Mondo Frizzatta - Cebolla y Queso Milanesa de soja "
#                                 "rellenas con cebolla y queso. Congelado. 4 unidades. "
#                                 "380 Grs")
#         p2 = self.qs.get(descripcion="Mondo Frizzatta - Choclo y Queso Milanesa de soja "
#                                      "rellenas con choclo y queso. Congelado. 4 unidades. "
#                                      "380 Grs")
#         self.assertGreater(p1.descripcion_distance, p2.descripcion_distance)

#     def test_de_la_milanga(self):
#         # esto deberia hacer explotar el equipo que hace el request
#         # por hereje. La "milanga" es de carne!
#         qs = self.f("milanga de soja")
#         self.assertTrue(qs.exists())

#     def test_cloro(self):
#         qs = self.f("cloro")
#         self.assertEqual(qs.count(), 2)


# class TestSimilaresAProducto(TestCase):

#     def setUp(self):
#         self.p1 = ProductoFactory(descripcion=u"Salsa de Tomate Arcor 500ml")
#         self.p2 = ProductoFactory(descripcion=u"Salsa de Tomate Cica 500ml")
#         self.p3 = ProductoFactory(descripcion=u"Puré de Tomate Arcor 350ml")
#         self.p4 = ProductoFactory(descripcion=u"Mayonesa Hellmanns 350gr")

#     @unittest.skip
#     def test_similares(self):
#         ids = self.p1.similares().values_list('id', flat=True)
#         self.assertEqual(list(ids), [self.p2.id, self.p3.id])

#         ids = self.p1.similares(1).values_list('id', flat=True)
#         self.assertEqual(list(ids), [self.p2.id])

#     @unittest.skip
#     def test_sin_resultado(self):
#         qs = self.p4.similares()
#         self.assertFalse(qs.exists())


class TestProductoBusqueda(TestCase):

    def test_acentos(self):
        p1 = ProductoFactory(descripcion=u"ÁéíóÚ")
        self.assertEqual(p1.busqueda, 'aeiou')

    def test_mayus(self):
        p1 = ProductoFactory(descripcion=u"UÑAS Y DIENTES")
        self.assertEqual(p1.busqueda, 'unas y dientes')


class TestDescripcionAlternativa(TestCase):

    def setUp(self):
        self.p1 = ProductoFactory(descripcion=u"Salsa de Tomate Arcor 500ml")

    def test_alternativa_guarda_instancia(self):
        assert DescripcionAlternativa.objects.count() == 0
        descripcion = "La misma salsa descripta distinto ;-)"
        self.p1.agregar_descripcion(descripcion)

        self.assertEqual(DescripcionAlternativa.objects.count(), 1)
        alternativa = DescripcionAlternativa.objects.all()[0]
        self.assertEqual(alternativa.producto, self.p1)
        self.assertEqual(alternativa.descripcion, descripcion)
        self.assertEqual(alternativa.busqueda, normalizar(descripcion))

    def test_excepcion_si_existe(self):
        descripcion = "La misma salsa descripta distinto ;-)"
        self.p1.agregar_descripcion(descripcion)
        with self.assertRaises(IntegrityError):
            self.p1.agregar_descripcion(descripcion)

    def test_ignorar_excepcion(self):
        descripcion = "La misma salsa descripta distinto ;-)"
        self.p1.agregar_descripcion(descripcion)
        # sin excepcion
        self.p1.agregar_descripcion(descripcion, True)
        self.assertEqual(DescripcionAlternativa.objects.count(), 1)


