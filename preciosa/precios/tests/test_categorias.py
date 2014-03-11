# -*- coding: utf-8 -*-
from django.test import TestCase
from preciosa.precios.models import Categoria


class TestCategoriaOculta(TestCase):

    def setUp(self):
        self.root = Categoria.add_root(nombre='root')
        self.root2 = Categoria.add_root(nombre='root 2')
        self.hija = self.root.add_child(nombre='hija')
        self.hija2 = self.root.add_child(nombre='hija 2')  # sin descendencia
        self.nieta = self.hija.add_child(nombre='nieta')
        self.nieta2 = self.hija.add_child(nombre='nieta2')

    def assertOcultoTrue(self, c):
        self.assertTrue(c.reload().oculta)

    def assertOcultoFalse(self, c):
        self.assertFalse(c.reload().oculta)

    def test_cambia_root(self):
        self.root.set_oculta(True)
        self.assertOcultoTrue(self.root)
        self.assertOcultoTrue(self.hija)
        self.assertOcultoTrue(self.hija2)
        self.assertOcultoTrue(self.nieta)
        self.assertOcultoTrue(self.nieta2)
        self.assertOcultoFalse(self.root2)

    def test_cambia_hija(self):
        self.hija.set_oculta(True)
        self.assertOcultoFalse(self.root)
        self.assertOcultoFalse(self.root2)
        self.assertOcultoTrue(self.hija)
        self.assertOcultoFalse(self.hija2)
        self.assertOcultoTrue(self.nieta)
        self.assertOcultoTrue(self.nieta2)

    def test_cambia_nieta(self):
        self.nieta.set_oculta(True)
        self.assertOcultoFalse(self.root)
        self.assertOcultoFalse(self.root2)
        self.assertOcultoFalse(self.hija)
        self.assertOcultoFalse(self.hija2)
        self.assertOcultoTrue(self.nieta)
        self.assertOcultoFalse(self.nieta2)


class TestCategoriaBusqueda(TestCase):

    def setUp(self):
        self.root = Categoria.add_root(nombre=u'Raíz 1')
        self.hija = self.root.add_child(nombre=u'Hija ñoña 2')
        self.nieta = self.hija.add_child(nombre='Nieta')

    def test_root(self):
        self.assertEqual(self.root.busqueda, 'raiz 1')

    def test_hija(self):
        self.assertEqual(self.hija.busqueda, 'raiz 1 hija nona 2')

    def test_nieta(self):
        self.assertEqual(self.nieta.busqueda, 'raiz 1 hija nona 2 nieta')

    def test_cambia_nieta(self):
        self.nieta.nombre = u'Nieta Queridísima'
        self.nieta.save()
        self.assertEqual(self.nieta.busqueda, 'raiz 1 hija nona 2 nieta queridisima')
        self.assertEqual(self.hija.busqueda, 'raiz 1 hija nona 2')

    def test_cambia_root(self):
        self.root.nombre = u'Raíz cuadrada'
        self.root.save()
        self.assertEqual(self.root.busqueda, 'raiz cuadrada')
        self.assertEqual(self.hija.reload().busqueda, 'raiz cuadrada hija nona 2')
        self.assertEqual(self.nieta.reload().busqueda, 'raiz cuadrada hija nona 2 nieta')
