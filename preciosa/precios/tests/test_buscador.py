# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from preciosa.precios.tests.factories import ProductoFactory


class TestBuscador(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('autocomplete_buscador')
        self.productos = [ProductoFactory(descripcion=u"Salsa de Tomate Arcor 500ml"),
                          ProductoFactory(descripcion=u"Salsa de Tomate Cica 500ml"),
                          ProductoFactory(descripcion=u"Pure de Tomate Arcor 350ml"),
                          ProductoFactory(descripcion=u"Mayonesa Hellmanns 350gr")]

    def assertResult(self, response, p):
        self.assertIn(p.descripcion, response.content)
        self.assertIn(p.get_absolute_url(), response.content)

    def assertNotResult(self, response, p):
        self.assertNotIn(p.descripcion, response.content)
        self.assertNotIn(p.get_absolute_url(), response.content)

    def test_js_requerido(self):
        base = render_to_string('base.html', {})
        buscador = render_to_string('_buscador.html', {})
        self.assertIn(buscador, base)
        self.assertIn("url: '%s'" % self.url, buscador)

    def test_busca_productos(self):
        mayo = self.productos[-1]
        response = self.client.get(self.url, {'q': 'tomate'})
        for p in self.productos[:-1]:
            self.assertResult(response, p)
        self.assertNotResult(response, mayo)

    def test_busca_por_palabras(self):
        for q in ('salsa cica', 'cica', 'tomate cica', 'cica tomate'):
            prods = self.productos[:]
            response = self.client.get(self.url, {'q': q})
            cica = prods[1]
            assert 'Cica' in cica.descripcion
            self.assertResult(response, cica)
            del prods[prods.index(cica)]
            for p in prods:
                self.assertNotResult(response, p)

    def test_busca_por_similaridad(self):
        response = self.client.get(self.url, {'q': 'salsa de tomate cica'})
        arcor = self.productos[0]
        assert 'Arcor' in arcor.descripcion
        self.assertResult(response, arcor)

    def test_busca_por_upc(self):
        arcor = self.productos[0]
        arcor.upc = '7790001184'
        arcor.save()
        response = self.client.get(self.url, {'q': '7790'})
        self.assertResult(response, arcor)
        for p in self.productos[1:]:
            self.assertNotResult(response, p)


