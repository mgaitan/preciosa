# -*- coding: utf-8 -*-
import unittest
from django.test import TestCase
from django.db import IntegrityError
from preciosa.precios.models import Producto, DescripcionAlternativa
from preciosa.precios.tests.factories import ProductoFactory, CategoriaFactory
from tools.texto import normalizar


class TestProductoDetail(TestCase):
    def setUp(self):
        self.p1 = ProductoFactory(descripcion=u"Salsa de Tomate Arcor 500ml")

    def test_detail_view_use_correct_template(self):
        response = self.client.get(self.p1.get_absolute_url())
        self.assertTemplateUsed(response, 'precios/detalle_producto.html')


class TestSimilaresAProducto(TestCase):

    def setUp(self):
        self.p1 = ProductoFactory(descripcion=u"Salsa de Tomate Arcor 500ml")
        self.p2 = ProductoFactory(descripcion=u"Salsa de Tomate Cica 500ml")
        self.p3 = ProductoFactory(descripcion=u"Puré de Tomate Arcor 350ml")
        self.p4 = ProductoFactory(descripcion=u"Mayonesa Hellmanns 350gr")

    @unittest.skip
    def test_similares(self):
        ids = self.p1.similares().values_list('id', flat=True)
        self.assertEqual(list(ids), [self.p2.id, self.p3.id])

        ids = self.p1.similares(1).values_list('id', flat=True)
        self.assertEqual(list(ids), [self.p2.id])

    @unittest.skip
    def test_sin_resultado(self):
        qs = self.p4.similares()
        self.assertFalse(qs.exists())


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


