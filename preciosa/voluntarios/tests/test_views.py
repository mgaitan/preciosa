# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from preciosa.precios.models import Cadena, Sucursal
from preciosa.precios.tests.factories import CityFactory


class VoluntariosTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='user_preciosa')
        self.user.set_password('pass')
        self.user.save()

        # Creamos algunas ciudades
        self.ciudad1 = CityFactory()
        self.ciudad2 = CityFactory()
        self.client = Client()
        #self.client.defaults = {'REMOTE_ADDR': 'localhost'}

    def test_views_cadena(self):
        # Nos logueamos con redirección al dashboard de voluntarios
        response = self.client.post('/account/login/?next={}'.format(reverse('voluntarios_dashboard')),
                                    {'username': self.user.username, 'password': 'pass'})
        self.assertRedirects(response, reverse('voluntarios_dashboard'))
        # accedemos al alta de cadenas y sucursales
        url_form = reverse('alta_cadena_sucursal')
        response = self.client.get(url_form)
        self.assertEqual(response.status_code, 200)
        # Creamos una nueva cadena
        response = self.client.post(url_form,
                                    {'nombre': 'cadena1', 'btn_form_cadena': 'Agregar'})
        self.assertEqual(response.status_code, 302)
        cadena1 = Cadena.objects.filter(nombre='Cadena1')
        self.assertTrue(cadena1.count() == 1)
        # Creamos una cadena con la anterior como su 'cadena_madre'
        response = self.client.post(url_form, data={
            'nombre': 'cadena2', 'btn_form_cadena': 'Agregar',
            'cadena_madre': cadena1[0].pk})
        self.assertEqual(response.status_code, 302)
        cadena2 = Cadena.objects.filter(nombre='Cadena2')
        self.assertTrue(cadena2.count() == 1)
        self.assertTrue(cadena2[0].cadena_madre.pk == cadena1[0].pk)
        # No puedo crear d)s cadenas con el mismo nombre
        response = self.client.post(url_form,
                                    {'nombre': 'cadena1', 'btn_form_cadena': 'Agregar'})
        self.assertEqual(response.status_code, 200)
        cadena1 = Cadena.objects.filter(nombre='Cadena1')
        # Sigue habiendo sólo una.
        self.assertTrue(cadena1.count() == 1)

    def test_view_alta_sucursales(self):
        self.client.login(username=self.user.username, password='pass')
        cadena1 = Cadena.objects.create(nombre=u'Cadena1')
        cadena1.save()
        url_form = reverse('alta_cadena_sucursal')
        # Creamos una sucursal de cadena1
        response = self.client.post(url_form, data={
            'cadena': cadena1.pk, 'nombre': u'', 'direccion': u'La calle #nn',
            'ciudad': self.ciudad1.pk, 'btn_form_sucursal': u'',
            'cp': u'', 'telefono': u'', 'horarios': u''})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Sucursal.objects.filter(cadena=cadena1.pk).exists())

        # Creamos una sucursal nombre propio sin cadena relacionada
        response = self.client.post(url_form, data={
            'cadena': u'', 'nombre': u'Don Pepe', 'direccion': u'El callejón #mm',
            'ciudad': self.ciudad1.pk, 'btn_form_sucursal': u''})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Sucursal.objects.filter(nombre='Don Pepe').exists())

        # Intentamos crear una sucursal sin campos requeridos
        response = self.client.post(url_form, data={
            'cadena': u'', 'nombre': u'', 'direccion': u'Callecita',
            'ciudad': self.ciudad1.pk, 'btn_form_sucursal': u'Agregar'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form_sucursal', '__all__',
                             u'Indique la cadena o el nombre del comercio')
        response = self.client.post(url_form, data={
            'cadena': u'', 'nombre': 'nombre', 'direccion': u'',
            'ciudad': self.ciudad2.pk, 'btn_form_sucursal': u'Agregar'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form_sucursal', '__all__',
                             u'La sucursal debe ser online o tener direccion física, pero no ambas')
        response = self.client.post(url_form, data={
            'cadena': u'', 'nombre': u'nombre', 'direccion': u'Callecita',
            'btn_form_sucursal': u'Agregar'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form_sucursal', 'ciudad', 'Este campo es obligatorio.')
