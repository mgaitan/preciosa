# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from preciosa.precios.tests.factories import ProductoFactory


class TestBuscador(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('autocomplete_buscador')

    def test_js_requerido(self):
        base = render_to_string('base.html', {})
        buscador = render_to_string('_buscador.html', {})
        self.assertIn(buscador, base)
        self.assertIn("url: '%s'" % self.url, buscador)

    def test_busca_productos(self):
        productos = [ProductoFactory(descripcion=u"Salsa de Tomate Arcor 500ml"),
                     ProductoFactory(descripcion=u"Salsa de Tomate Cica 500ml"),
                     ProductoFactory(descripcion=u"Pure de Tomate Arcor 350ml"),
                     ProductoFactory(descripcion=u"Mayonesa Hellmanns 350gr")]
        mayo = productos[-1]
        response = self.client.get(self.url, {'q': 'tomate'})
        for p in productos[:-1]:
            self.assertIn(p.descripcion, response.content)
            self.assertIn(p.get_absolute_url(), response.content)
        self.assertNotIn(mayo.descripcion, response.content)
        self.assertNotIn(mayo.get_absolute_url(), response.content)


