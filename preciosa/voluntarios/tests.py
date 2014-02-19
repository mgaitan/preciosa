# -*- coding: utf-8 -*-
from django.test import TestCase

from preciosa.voluntarios.forms import (MarcaModelForm,
                                        EmpresaFabricanteModelForm)
from preciosa.precios.tests.factories import (MarcaFactory,     # noqa
                                              EmpresaFabricanteFactory)


class TestMarcaModelForm(TestCase):
    factory = MarcaFactory

    def setUp(self):
        self.FormClass = MarcaModelForm
        self.fabricante = EmpresaFabricanteFactory()
        self.form = self.FormClass()

    def test_campos_requeridos(self):
        f = self.form
        self.assertTrue(f.fields['fabricante'].required)
        self.assertTrue(f.fields['nombre'].required)

    def _post(self, nombre):
        f = self.FormClass({'fabricante': self.fabricante.id,
                            'nombre': nombre})
        return f

    def test_numeros(self):
        f = self._post('10 de 2013')

        self.assertFalse(f.is_valid())
        self.assertIn(u'demasiados números', f.errors['nombre'][0])

    def test_caracteres(self):
        f = self._post(u'Marca ®')
        self.assertFalse(f.is_valid())
        self.assertIn(u'caracter extraño', f.errors['nombre'][0])

    def test_muchas_palabras(self):
        f = self._post(u'una marca muy larga')
        self.assertFalse(f.is_valid())
        self.assertIn(u'demasiadas palabras', f.errors['nombre'][0])

    def test_existe(self):
        instance = self.factory()
        f = self._post('   ' + instance.nombre.lower() + '   ')
        self.assertFalse(f.is_valid())
        self.assertIn(u'no existe ya?', f.errors['nombre'][0])

    def test_valido1(self):
        f = self._post('9 de oro')
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data['nombre'], '9 de Oro')

    def test_valido2(self):
        f = self._post('la morenita')
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data['nombre'], 'La Morenita')

    def test_valido3(self):
        f = self._post('COCA COLA')
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data['nombre'], 'Coca Cola')


class TestEmpresaFabricanteModelForm(TestMarcaModelForm):
    factory = EmpresaFabricanteFactory

    def setUp(self):

        self.form = EmpresaFabricanteModelForm()

    def _post(self, nombre):
        f = EmpresaFabricanteModelForm({'nombre': nombre})
        return f

    def test_campos_requeridos(self):
        f = self.form
        self.assertTrue(f.fields['nombre'].required)
