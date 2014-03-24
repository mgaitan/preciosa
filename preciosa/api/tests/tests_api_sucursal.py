# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from mock import patch, MagicMock
from datetime import datetime
from decimal import Decimal
from preciosa.precios.models import Precio
from preciosa.precios.tests.factories import (SucursalFactory,
                                              ProductoFactory, PrecioFactory)
from tools.gis import punto_destino


class TestsApiSucursal(APITestCase):

    def setUp(self):
        self.suc = SucursalFactory()
        self.url = reverse('sucursales')

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


class TestsDetalle(APITestCase):

    def setUp(self):
        self.suc = SucursalFactory()
        self.prod = ProductoFactory(upc='779595')
        self.url = reverse('producto_detalle', args=(self.suc.id, self.prod.id))

    def test_detalle_producto(self):
        r = self.client.get(self.url)
        prod = r.data['producto']
        self.assertEqual(prod['id'], self.prod.id)
        self.assertEqual(prod['descripcion'],
                         self.prod.descripcion)
        self.assertEqual(prod['upc'],
                         self.prod.upc)

    def test_detalle_similares(self):
        simil1 = ProductoFactory(descripcion=self.prod.descripcion + " plus")
        simil2 = ProductoFactory(descripcion=self.prod.descripcion + " extra")
        with patch('preciosa.precios.models.Producto.similares') as mock:
            mock.return_value = [simil1, simil2]
            r = self.client.get(self.url)
        similares = r.data['similares']
        self.assertEqual(similares[0]['id'], simil1.id)
        self.assertEqual(similares[0]['descripcion'], simil1.descripcion)
        self.assertEqual(similares[1]['id'], simil2.id)
        self.assertEqual(similares[1]['descripcion'], simil2.descripcion)

    def test_mas_probables(self):
        p1, p2 = mis_precios = [PrecioFactory(sucursal=self.suc,
                                              precio=12.2,
                                              producto=self.prod),
                                PrecioFactory(sucursal=self.suc,
                                              precio=14.4,
                                              producto=self.prod)]

        with patch('preciosa.precios.models.PrecioManager.mas_probables') as mock:
            mock.return_value = mis_precios
            r = self.client.get(self.url)
        mas_probables = r.data['mas_probables']
        self.assertEqual(mas_probables[0]['precio'], p1.precio)
        self.assertEqual(mas_probables[0]['created'], p1.created)
        self.assertEqual(mas_probables[1]['precio'], p2.precio)
        self.assertEqual(mas_probables[1]['created'], p2.created)

    def test_mejores(self):
        p1, p2 = mis_precios = [PrecioFactory(precio=12.2,
                                              producto=self.prod),
                                PrecioFactory(precio=14.4,
                                              producto=self.prod)]

        with patch('preciosa.precios.models.PrecioManager.mejores') as mock:
            mock.return_value = mis_precios
            r = self.client.get(self.url)

        mejores = r.data['mejores']
        self.assertEqual(mejores[0]['precio'], p1.precio)
        self.assertEqual(mejores[0]['created'], p1.created)
        self.assertEqual(mejores[0]['sucursal']['direccion'], p1.sucursal.direccion)
        self.assertEqual(mejores[1]['precio'], p2.precio)
        self.assertEqual(mejores[1]['created'], p2.created)
        self.assertEqual(mejores[1]['sucursal']['direccion'], p2.sucursal.direccion)

    def test_envio_precio(self):
        fecha = datetime(year=2014, month=3, day=22, hour=0, minute=1)
        r = self.client.post(self.url, {'precio': 10, 'created': fecha})
        self.assertEqual(r.status_code, 200)
        precio = Precio.objects.get()
        self.assertEqual(precio.precio, Decimal('10'))
        self.assertEqual(precio.producto, self.prod)
        self.assertEqual(precio.sucursal, self.suc)
        self.assertEqual(str(precio.created), str(fecha))

    def test_integracion(self):
        """1. se pide precio para un producto que aun no tiene precios
           2. se envia un precio para la sucursal A
           3. En otra sucursal B (cercana a B) y de la misma cadena, el precio
              enviado aparece como mas probable.
           4. En B se envia un precio mejor
           5. en la sucursal original A, el precio sigue siendo el enviado,
              pero aparece un mejor precio (el de B)
        """
        r = self.client.get(self.url)
        assert len(r.data['mas_probables']) == 0
        assert len(r.data['mejores']) == 0
        # se envia un precio original en A
        self.client.post(self.url, {'precio': 10})

        # ahora el mas probable y el mejor es 10
        r = self.client.get(self.url)
        self.assertEqual(r.data['mas_probables'][0]['precio'], 10.)
        self.assertEqual(r.data['mejores'][0]['precio'], 10.)

        # Se envia un mejor precio en la sucursal B
        suc_b = SucursalFactory(cadena=self.suc.cadena, ciudad=self.suc.ciudad,
                                ubicacion=punto_destino(self.suc.ubicacion,
                                                        90, 1))
        url_b = reverse('producto_detalle', args=(suc_b.id, self.prod.id))
        rb = self.client.get(url_b)

        # no hay precios en esta suc
        assert Precio.objects.filter(sucursal=suc_b).count() == 0

        # pero el mas probable es el enviado en A
        self.assertEqual(rb.data['mas_probables'][0]['precio'], 10)

        # se envia un precio nuevo, mejor
        self.client.post(url_b, {'precio': 8})

        # de nuevo en la sucursal A, el precio se mantiene, pero hay mejor
        r = self.client.get(self.url)
        self.assertEqual(r.data['mas_probables'][0]['precio'], 10.)
        self.assertEqual(r.data['mejores'][0]['precio'], 8)

