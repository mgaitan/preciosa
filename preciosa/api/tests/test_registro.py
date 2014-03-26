# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.core.serializers import serialize
from rest_framework import status
from preciosa.precios.tests.factories import UserFactory
from preciosa.api.models import MovilInfo
from preciosa.api.tests.factories import MovilInfoFactory

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

    def test_obtiene_usuario_existente_via_uuid(self):

        movil_info = MovilInfoFactory()
        movil_info.user
        assert User.objects.count() == 1
        assert MovilInfo.objects.count() == 1

        antes = serialize('json', User.objects.all())

        data = {'uuid': movil_info.uuid}
        r = self.client.post(self.url, data)
        # no cambio
        self.assertEqual(serialize('json', User.objects.all()), antes)
        user = User.objects.get()
        self.assertEqual(r.data['token'], user.auth_token.key)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # no se crean nuevos movil_info
        self.assertEqual(MovilInfo.objects.count(), 1)

    def test_not_auth_con_uuid_no_existente_crea_usuario_y_movil_info(self):
        assert User.objects.count() == 0
        assert MovilInfo.objects.count() == 0

        data = {'uuid': 'uuid-re-loco'}
        r = self.client.post(self.url, data)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        user = User.objects.get()
        self.assertEqual(r.data['token'], user.auth_token.key)
        self.assertEqual(user.movil_info.count(), 1)
        self.assertEqual(user.movil_info.get().uuid, 'uuid-re-loco')

    def test_si_existe_movil_info_se_guarda(self):
        data = {'uuid': 'uuid-re-loco',
                'phonegap': '3.3',
                'nombre': 'Passion',  # nexus one
                'plataforma': 'Android',
                'plataforma_version': '2.3',
                'preciosa_version': '0.1 (natimit)'}
        self.client.post(self.url, data)
        movil_info = User.objects.get().movil_info.get()
        self.assertEqual(movil_info.uuid, 'uuid-re-loco')
        self.assertEqual(movil_info.phonegap, '3.3')
        self.assertEqual(movil_info.nombre, 'Passion')
        self.assertEqual(movil_info.plataforma, 'Android')
        self.assertEqual(movil_info.plataforma_version, '2.3')
        self.assertEqual(movil_info.preciosa_version, '0.1 (natimit)')


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

    def test_si_existe_movil_info_se_guarda(self):
        data = {'uuid': 'uuid-re-loco', 'phonegap': '3.3',
                'nombre': 'Passion',  # nexus one
                'plataforma': 'Android',
                'plataforma_version': '2.3',
                'preciosa_version': '0.1 (natimit)'}
        self.client.post(self.url, data)
        movil_info = User.objects.get().movil_info.get()
        self.assertEqual(movil_info.user, self.user)
        self.assertEqual(movil_info.uuid, 'uuid-re-loco')
        self.assertEqual(movil_info.phonegap, '3.3')
        self.assertEqual(movil_info.nombre, 'Passion')
        self.assertEqual(movil_info.plataforma, 'Android')
        self.assertEqual(movil_info.plataforma_version, '2.3')
        self.assertEqual(movil_info.preciosa_version, '0.1 (natimit)')
