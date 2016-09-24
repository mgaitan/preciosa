# -*- coding: utf-8 -*-
import unittest
from collections import OrderedDict
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from mock import patch
from datetime import datetime
from decimal import Decimal
from preciosa.precios.models import Precio
from preciosa.precios.tests.factories import (SucursalFactory, UserFactory,
                                              ProductoFactory, PrecioFactory)
from tools.gis import punto_destino


class TestsDetalle(APITestCase):

    def setUp(self):
        self.suc = SucursalFactory()
        self.prod = ProductoFactory(upc='779595')
        self.url = reverse('producto_detalle', args=(self.suc.id, self.prod.id))
        self.user = UserFactory()
        self.token = self.user.auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_requiere_auth(self):
        self.client.credentials()  # borra token
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('creden', r.data['detail'])

    def test_auth_puede_ser_por_query(self):
        self.client.credentials()  # borra token
        r = self.client.get(self.url + '?token=' + self.token)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

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

    @unittest.skip
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
        self.assertEqual(mas_probables[1]['precio'], p2.precio)


    def test_mejores(self):
        p1, p2 = mis_precios = [PrecioFactory(precio='12.20',
                                              producto=self.prod),
                                PrecioFactory(precio='14.40',
                                              producto=self.prod)]

        with patch('preciosa.precios.models.PrecioManager.mejores') as mock:
            mock.return_value = mis_precios
            r = self.client.get(self.url)

        mejores = r.data['mejores']
        self.assertEqual(mejores[0]['precio'], p1.precio)
        self.assertEqual(mejores[0]['sucursal']['direccion'], p1.sucursal.direccion)
        self.assertEqual(mejores[1]['precio'], p2.precio)
        self.assertEqual(mejores[1]['sucursal']['direccion'], p2.sucursal.direccion)

    def test_sin_acuerdo(self):
        r = self.client.get(self.url)
        self.assertEqual(r.data['en_acuerdo'], [])

    def test_producto_en_acuerdo(self):
        with patch('preciosa.acuerdos.models.PrecioEnAcuerdoManager.en_acuerdo') as mock:
            mock.return_value = [{'acuerdo__nombre': u'Precios culiados',
                                  'precio': Decimal('123.30')}]
            r = self.client.get(self.url)
        en_acuerdo = r.data['en_acuerdo']
        self.assertEqual(en_acuerdo, [OrderedDict([('nombre', u'Precios culiados'),
                                                   ('precio', u'123.30')])])

    def test_envio_precio(self):
        fecha = datetime(year=2014, month=3, day=22, hour=0, minute=1)
        r = self.client.post(self.url, {'precio': 10, 'created': fecha})
        self.assertEqual(r.status_code, 200)
        precio = Precio.objects.get()
        self.assertEqual(precio.precio, Decimal('10'))
        self.assertEqual(precio.producto, self.prod)
        self.assertEqual(precio.sucursal, self.suc)
        self.assertEqual(precio.usuario, self.user)
        self.assertEqual(str(precio.created), str(fecha))

    def test_ignora_precio_0(self):
        assert Precio.objects.count() == 0
        self.client.post(self.url, {'precio': '0.0'})
        self.assertEqual(Precio.objects.count(), 0)

    def test_ignora_precio_con_diferencia_del_50(self):
        PrecioFactory(sucursal=self.suc, precio=10, producto=self.prod)
        assert Precio.objects.count() == 1
        self.client.post(self.url, {'precio': 15.1})
        self.assertEqual(Precio.objects.count(), 1)
        self.client.post(self.url, {'precio': 14.9})
        self.assertEqual(Precio.objects.count(), 2)

    @unittest.skip
    def test_integracion(self):
        """1. se pide precio para un producto que aun no tiene precios
           2. se envia un precio para la sucursal A
           3. En otra sucursal B (cercana a A) y de la misma cadena, el precio
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

    @unittest.skip
    def test_integracion_2(self):
        """igual, pero la sucursal b es de otra ciudad.
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

        suc_b = SucursalFactory(cadena=self.suc.cadena,
                                ubicacion=punto_destino(self.suc.ubicacion,
                                                        90, 1))
        assert suc_b.ciudad != self.suc.ciudad
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


class TestsDetalleCoord(APITestCase):

    def setUp(self):
        self.suc = SucursalFactory()
        self.prod = ProductoFactory(upc='779595')
        self.url = reverse('producto_detalle_coor', args=(self.prod.id,))
        self.user = UserFactory()
        self.token = self.user.auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_requiere_auth(self):
        self.client.credentials()  # borra token
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('creden', r.data['detail'])

    def test_auth_puede_ser_por_query(self):
        self.client.credentials()  # borra token
        r = self.client.get(self.url + '?token=' + self.token)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_detalle_producto(self):
        r = self.client.get("%s?lat=-32.000&lng=-45.000" % self.url)
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
            r = self.client.get("%s?lat=-32.000&lng=-45.000" % self.url)
        similares = r.data['similares']
        self.assertEqual(similares[0]['id'], simil1.id)
        self.assertEqual(similares[0]['descripcion'], simil1.descripcion)
        self.assertEqual(similares[1]['id'], simil2.id)
        self.assertEqual(similares[1]['descripcion'], simil2.descripcion)
