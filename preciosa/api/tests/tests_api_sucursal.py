# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from mock import patch, MagicMock
from preciosa.precios.tests.factories import UserFactory, SucursalFactory
from tools.gis import punto_destino


class TestsApiSucursal(APITestCase):

    def setUp(self):
        self.suc = SucursalFactory()
        self.url = reverse('sucursales')
        self.token = UserFactory().auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_requiere_auth(self):
        self.client.credentials()  # borra token
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('credentials', r.data['detail'])

    def test_auth_puede_ser_por_query(self):
        self.client.credentials()  # borra token
        r = self.client.get(self.url + '?token=' + self.token)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_muestra_lista(self):
        suc2 = SucursalFactory()
        response = self.client.get(self.url)
        for suc, js in zip((self.suc, suc2), response.data['results']):
            self.assertEqual(js['id'], suc.id)
            self.assertEqual(js['cadena']['id'], suc.cadena.id)
            self.assertEqual(js['ubicacion'], str(suc.ubicacion))
            self.assertEqual(js['direccion'], suc.direccion)

    def test_muestra_detalle(self):
        url_detalle = reverse('sucursal_detalle', args=(self.suc.id,))
        response = self.client.get(url_detalle)
        js = response.data
        self.assertEqual(js['id'], self.suc.id)
        self.assertEqual(js['cadena']['id'], self.suc.cadena.id)
        self.assertEqual(js['ubicacion'], str(self.suc.ubicacion))
        self.assertEqual(js['direccion'], self.suc.direccion)

    def test_parametro_q_usa_buscador(self):
        with patch('preciosa.precios.models.SucursalQuerySet.buscar') as mock:
            self.client.get(self.url, data={'q': 'hola'})
        mock.assert_called_once_with('hola')

    def test_parametros_lon_lat_radio_filtra_por_ubicacion(self):
        p = punto_destino(self.suc.ubicacion, 90, 1)
        lon, lat = p.x, p.y
        with patch('preciosa.precios.models.SucursalQuerySet.alrededor_de') as mock:
            self.client.get(self.url, data={'lon': lon, 'lat': lat, 'radio': 2})
        p2 = mock.call_args[0][0]
        radio = mock.call_args[0][1]
        self.assertAlmostEqual(p2.x, lon)
        self.assertAlmostEqual(p2.y, lat)
        self.assertEqual(radio, 2.0)

    def test_lon_lan_y_radio_son_requeridos_todos(self):
        with patch('preciosa.precios.models.SucursalQuerySet.alrededor_de') as mock:
            self.client.get(self.url, data={'lon': 1, 'radio': 19})
        self.assertFalse(mock.called)
        with patch('preciosa.precios.models.SucursalQuerySet.alrededor_de') as mock:
            self.client.get(self.url, data={'lat': 1})
        self.assertFalse(mock.called)

    def test_lon_lat_y_busqueda_a_la_vez(self):
        with patch('preciosa.precios.models.SucursalQuerySet.buscar') as mock_b:
            mock_a = MagicMock(name='mi_alrededor_de')
            mock_b.return_value.alrededor_de = mock_a
            self.client.get(self.url, data={'lon': 1, 'lat': -3, 'radio': 10,
                                            'q': 'zaraza'})
        mock_b.assert_called_once_with('zaraza')
        p = mock_a.call_args[0][0]
        radio = mock_a.call_args[0][1]
        self.assertAlmostEqual(p.x, 1)
        self.assertAlmostEqual(p.y, -3)
        self.assertEqual(radio, 10.0)       # default
