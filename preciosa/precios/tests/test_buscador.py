# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from preciosa.precios.tests.factories import ProductoFactory


class TestBuscador(TestCase):

    # TO DO: luego de #170 este testcase deberia comproboar los resultados
    # del metodo ``ProductoManager.buscar`` y no de la vista buscador

    def setUp(self):
        self.client = Client()
        self.url = reverse('buscador')
        self.productos = [ProductoFactory(descripcion=u"Salsa de Tomate Arcor 500ml"),
                          ProductoFactory(descripcion=u"Salsa de Tomate Cica 500ml"),
                          ProductoFactory(descripcion=u"Puré de Tomate Arcor 350ml"),
                          ProductoFactory(descripcion=u"Mayonesa Hellmanns 350gr")]

    def assertResult(self, response, p):
        self.assertIn({
            'id': p.id,
            'value': p.descripcion,
            'url': p.get_absolute_url()
        }, response.json()['results'])
        
    def assertNotResult(self, response, p):
        self.assertNotIn({
            'id': p.id,
            'value': p.descripcion,
            'url': p.get_absolute_url()
        }, response.json()['results'])

    def test_js_requerido(self):
        base = render_to_string('base.html', {})
        buscador = render_to_string('_buscador_js.html', {})
        self.assertIn(buscador, base)
        self.assertIn(self.url, buscador)

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

    def test_ignora_acentos(self):
        pure = self.productos[2]
        assert u'Puré' in pure.descripcion
        response = self.client.get(self.url, {'q': 'puré'})
        self.assertResult(response, pure)
        response = self.client.get(self.url, {'q': 'Pure  '})
        self.assertResult(response, pure)
