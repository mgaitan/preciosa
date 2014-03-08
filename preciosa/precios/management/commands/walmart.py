# -*- coding: utf-8 -*-
import logging
import json
import requests

from pyquery import PyQuery
from random import random
from preciosa.precios.models import Categoria, Producto, Sucursal, Precio

from django.core.management.base import BaseCommand

logger = logging.getLogger('Walmart')

WALMART_ONLINE = Sucursal.objects.get(nombre='Walmart Online')
BASEURL = "https://www.walmartonline.com.ar/"
#Detalle-de-articulo.aspx?upc="

class Command(BaseCommand):
    help = 'Scrap de Walmart'

    def handle(self, *args, **options):
        browser = requests.Session()
        browser.headers.update({'User-agent': 'Mozilla/5.0'})
        #Accedo al Home una vez para asentar las cookies

        browser.get(BASEURL)


        #Obtengo los Rubros disponibles
        RUBROS = "WebControls/hlMenuLeft.ashx"
        resp = browser.get(BASEURL + RUBROS)
        rubros = resp.json()
        precioscargados = 0
        productosnuevos = 0
        for departamento in rubros["MenuPrincipal"][0]['Elements']:
            departamentoname = departamento["departmentName"]
            for familia in departamento["Elements"]:
                familianame = familia["departmentName"]
                browser.get(BASEURL + "Busqueda.aspx?Departamento=%s&Familia=%s" % (departamentoname, familianame))
                headers = {"Referer" : BASEURL + "Busqueda.aspx?Departamento=%s" %  departamentoname}
                params = {"busqueda": "undefined", "departamento": departamentoname, "familia": familianame,
                          "linea": "undefined", "orderby": "undefined", "orderbyid": "undefine",
                          "range" : "undefined", "sid": (random()*3) }
                browser.get(BASEURL + "WebControls/hlSearchResults.ashx", params=params )
                resp = browser.get(BASEURL + "WebControls/hlSearchProducts.ashx", headers=headers)
                for prod in resp.json():
                    um = Producto.UM_TRANS.get(prod['WMNumber'],
                                               prod['WMNumber'])
                    prod["upc"] = prod["upc"].lstrip("0")
                    try:
                        producto = Producto.objects.get(upc=prod['upc'])
                    except Producto.DoesNotExist:
                        try:
                            proddata = self.parse(prod['upc'])
                            #print "Creando Productor %s" % str(prod)
                            producto = Producto.objects.create(descripcion=prod['Description'],
                                                   upc=prod['upc'],
                                                   unidad_medida=um,
                                                   categoria=proddata["categoria"],
                                                   notas='PrecioGranel: %s' % prod["PrecioGranel"],
                                                )
                            productosnuevos += 1
                        except ValueError:
                            print "**No se puede cargar el producto %s" % str(proddata)
                            continue
                    Precio.objects.create(producto=producto,
                                          sucursal=WALMART_ONLINE,
                                          precio=self.clean_precio(prod['Precio']))
                    precioscargados += 1
        print "Se cargaron precios para %d productos, y se agregaron %d productos nuevos" % (precioscargados, productosnuevos)

    def parse(self, upc):
        """dado un UPC, devuelve un diccionario de datos scrappeados
        de la pagina de detalle del producto"""

        def cat(pq):
            html_categ = [s.strip().lower() for s in pq('div.tituloNaranja').text().strip().split(u'\xa0>')
                          if s.strip()]
            match = Categoria.objects.filter(nombre__icontains=html_categ[-1])
            if len(match) == 1:
                return match[0]
            else:
                for m in match:
                    ancestors = [c.nombre.lower() for c in m.get_ancestors()]
                    if ancestors == html_categ[:2]:
                        return m

        pq = PyQuery(BASEURL + "Detalle-de-articulo.aspx?upc=%s" % upc)
        categoria = cat(pq)

        descripcion = pq('span#lblTitle').text()
        precio = self.clean_precio(pq('span#lblPrice').text())
        um = pq('span#lblUnit').text()
        um = Producto.UM_TRANS.get(um, um)
        notas = 'PrecioGranel: %s' % pq('span#lblPricexUnit').text()

        return {'categoria': categoria, 'descripcion': descripcion,
            'precio': precio, 'unidad_medida': um,
            'notas': notas, 'upc': upc}

    def clean_precio(self, precio):
        return precio.replace('$','').replace(',', '')

