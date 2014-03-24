# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.core.serializers import serialize
from rest_framework import status
from preciosa.precios.tests.factories import UserFactory

User = get_user_model()


class TestsRegistroNoAuth(APITestCase):

    def setUp(self):
        self.url = reverse('registro')

    def test_no_auth_sin_data_crea_user_anonimo(self):
        assert User.objects.count() == 0
        r = self.client.post(self.url)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(r.data['token'], user.auth_token.key)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_no_auth_con_data_crea_user(self):
        data = {'username': 'tin',
                'password': 'zaraza',
                'email': 'tin@zaraza.com'}
        r = self.client.post(self.url, data)
        user = User.objects.get()
        self.assertEqual(user.username, 'tin')
        self.assertEqual(user.email, 'tin@zaraza.com')
        self.assertTrue(user.check_password('zaraza'))
        self.assertEqual(r.data['token'], user.auth_token.key)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_no_auth_con_data_erronea_da_error(self):
        assert User.objects.count() == 0
        data = {'username': 'tin',
                'password_wrong': 'zaraza',
                'email': 'tin@zaraza.com'}
        r = self.client.post(self.url, data)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('password', r.data['detail'])
        self.assertIn('obligatorio', r.data['detail']['password'][0])

        self.assertEqual(User.objects.count(), 0)

    def test_no_auth_con_data_username_existente_error(self):
        UserFactory(username='tin', email='tin@zaraza.com')
        data = {'username': 'tin',
                'password': 'otro_pass',
                'email': 'otro_mail@zaraza.com'}
        r = self.client.post(self.url, data)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('username', r.data['detail'])
        self.assertIn('existe', r.data['detail']['username'][0])


class TestsRegistroAuth(APITestCase):

    def setUp(self):
        self.url = reverse('registro')
        self.user = UserFactory()
        self.token = self.user.auth_token.key
        # configura el cliente para que envie siempre el token en el header HTTP
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_auth_sin_data_solo_devuelve_el_token(self):
        antes = serialize('json', User.objects.all())
        r = self.client.post(self.url)
        self.assertEqual(r.data['token'], self.token)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # no cambió nada
        self.assertEqual(serialize('json', User.objects.all()), antes)

    def test_auth_con_data_actualiza_user(self):
        assert User.objects.count() == 1
        data = {'username': 'tin',
                'password': 'zaraza',
                'email': 'tin@zaraza.com'}
        r = self.client.post(self.url, data)

        self.assertEqual(r.data['token'], self.token)
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

        # no se creó ningun usuario nuevo
        self.assertEqual(User.objects.count(), 1)

        # se actualizó
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.username, 'tin')
        self.assertEqual(user.email, 'tin@zaraza.com')
        self.assertTrue(user.check_password('zaraza'))

    def test_auth_con_data_erronea_da_error(self):
        antes = serialize('json', User.objects.all())
        data = {'username_wrong': 'tin',
                'password': 'zaraza',
                'email': 'tin@zaraza.com'}
        r = self.client.post(self.url, data)
        self.assertEqual(serialize('json', User.objects.all()), antes)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('username', r.data['detail'])
        self.assertIn('obligatorio', r.data['detail']['username'][0])

