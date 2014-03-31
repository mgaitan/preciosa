# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from mock import patch, MagicMock
from preciosa.precios.models import Sucursal
from preciosa.precios.tests.factories import UserFactory, SucursalFactory, CityFactory
from tools.gis import punto_destino


class BaseTestApiSucursal(APITestCase):

    def setUp(self):
        self.suc = SucursalFactory()
        self.url = reverse('sucursales')
        self.token = UserFactory().auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)


class TestsListaSucursal(BaseTestApiSucursal):

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
            self.assertEqual(js['cadena'], suc.cadena.id)
            self.assertEqual(js['cadena_completa']['id'], suc.cadena.id)
            self.assertEqual(js['ubicacion'], str(suc.ubicacion))
            self.assertEqual(js['direccion'], suc.direccion)

    def test_muestra_detalle(self):
        url_detalle = reverse('sucursal_detalle', args=(self.suc.id,))
        response = self.client.get(url_detalle)
        js = response.data
        self.assertEqual(js['id'], self.suc.id)
        self.assertEqual(js['cadena'], self.suc.cadena.id)
        self.assertEqual(js['cadena_completa']['id'], self.suc.cadena.id)
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

    def test_no_muestra_sucursales_online(self):
        self.suc.online = True
        self.suc.save()
        response = self.client.get(self.url)
        self.assertEqual(response.data['results'], [])


class TestsCrearSucursal(BaseTestApiSucursal):

    def test_crear_nueva_sucursal(self):
        assert self.suc.cadena.id
        ciudad = CityFactory()

        r = self.client.post(self.url, {'cadena': self.suc.cadena.id,
                                        'nombre': 'zaraza',
                                        'ciudad': ciudad.id,
                                        'direccion': u'durazno y convencion'})

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sucursal.objects.count(), 2)
        self.assertEqual(r.data['cadena'], self.suc.cadena.id)
        self.assertEqual(r.data['direccion'], u'durazno y convencion')
        nueva = Sucursal.objects.get(id=r.data['id'])
        self.assertEqual(nueva.cadena, self.suc.cadena)
        self.assertEqual(nueva.direccion, u'durazno y convencion')

    def test_crear_nueva_sucursal_data_invalida(self):
        r = self.client.post(self.url, {'nombre': 'zaraza',
                                        'ciudad': 1354,
                                        'direccion': u'durazno y convencion'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data,
                         {'ciudad': [u"Invalid pk '1354' - object does not exist."]})

    def test_crear_nueva_sucursal_cadena_vacia(self):
        r = self.client.post(self.url, {'cadena': '',
                                        'nombre': 'zaraza',
                                        'ciudad': self.suc.ciudad.id,
                                        'direccion': u'durazno y convencion'})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        nueva = Sucursal.objects.get(id=r.data['id'])
        self.assertIsNone(nueva.cadena)

    def test_crear_nueva_sucursal_cadena_otra(self):
        r = self.client.post(self.url, {'cadena': 'otra',
                                        'nombre': 'zaraza',
                                        'ciudad': self.suc.ciudad.id,
                                        'direccion': u'durazno y convencion'})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        nueva = Sucursal.objects.get(id=r.data['id'])
        self.assertIsNone(nueva.cadena)

    def test_crear_nueva_sucursal_sin_clave_cadena(self):
        r = self.client.post(self.url, {'nombre': 'zaraza',
                                        'ciudad': self.suc.ciudad.id,
                                        'direccion': u'durazno y convencion'})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        nueva = Sucursal.objects.get(id=r.data['id'])
        self.assertIsNone(nueva.cadena)

    def test_crear_nueva_sucursal_ubicacion(self):
        for ubic in ['33.56 18.5', 'POINT (33.56 18.5)',
                     'lon:33.56 lat:18.5', '33.56, 18.5']:
            Sucursal.objects.all().delete()
            r = self.client.post(self.url, {'nombre': 'zaraza',
                                            'ciudad': self.suc.ciudad.id,
                                            'direccion': u'durazno y convencion',
                                            'ubicacion': ubic})
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            nueva = Sucursal.objects.get(id=r.data['id'])
            self.assertEqual(nueva.lon, 33.56)
            self.assertEqual(nueva.lat, 18.5)
