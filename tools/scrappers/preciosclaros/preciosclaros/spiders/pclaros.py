# -*- coding: utf-8 -*-
import json
from datetime import datetime
import scrapy
from preciosclaros.items import SucursalItem, ProductoItem, PrecioItem


HEADERS = {'x-api-key': 'PkVRKmPu0k6O2F0Y9J78TaFekqe3mAAe3RWJ5Vaj',
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.89 Safari/537.36'}

base_url = 'https://d3e6htiiul5ek9.cloudfront.net/'
sucursales_url = base_url + 'prod/sucursales'     # ?limit=50&offset=50
productos_url = base_url + 'prod/productos'  # ?id_sucursal


# en su membresia gratuita de Scrapinghub se impone un limite de 24hs de ejecucion por job,
# y en ese periodo se obtienen 4millones de items, que es aproximadamente la mitad de los datos que ofrece
# el portal precios claros
#
# Haciendo un *abuso bienintencionado* (?), lo que hago es dividir es obtener 1/7 partes del dataset
# (aproximadamente) por cada ejecucion, a traves de un argumento que se pasa el scrapper,
# programando la corrida de una porcion diferente cada dia.
#
# Note: seria más simple directamente separar "la porcion" a recorrer en un unico spider en funcion del dia en
# que se corre`(e.j `` datetime.datetime.today().weekday()``), pero de esta manera se puede incluso programar
# más de una instancia, pudiendo tener jobs simultaneos de distintos spiders, lo que aumentaria la frecuencia
#
TOTAL_SPIDERS = 7
LIMIT = 50


class PreciosClarosSpider(scrapy.Spider):
    name = "preciosclaros"

    def __init__(self, porcion=0, *args, **kwargs):
        self.porcion = porcion
        super(PreciosClarosSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(url=sucursales_url + '?limit=50',
                             callback=self.parse_sucursal_first_page,
                             headers=HEADERS)

    def parse_sucursal_first_page(self, response):
        """
        a traves del response de la primer pagina ``sucursales_url`` obtiene el total de sucursales y
        calcula cada peticion secuencialmente.

        el total se divide en la cantidad de spiders y se redondea para que
        cada cada uno scrappee su "grupo" de sucursales,
        en páginas de tamaño ``LIMIT``
        """
        json_data = json.loads(response.text)
        total = json_data['total']

        sucursales_por_spider = (total / TOTAL_SPIDERS // LIMIT) * LIMIT
        start = sucursales_por_spider * int(self.porcion)
        end = start + sucursales_por_spider

        # process pages
        for offset in xrange(start, end, LIMIT):
            yield scrapy.Request(url=sucursales_url + '?limit={}&offset={}'.format(LIMIT, offset),
                                 callback=self.parse_sucursal,
                                 headers=HEADERS, meta={'offset': offset, 'end': end})

    def parse_sucursal(self, response):
        """Este metodo es el parser real de la pagina para obtener sucursales.
        El item se interpreta *as is* como lo ofrece la API.

        Luego, por cada sucursal se genera un request a la primer pagina de los productos
        """

        json_data = json.loads(response.text)
        self.logger.info('Obteniendo sucursales %s/%s', response.meta.get('offset'), response.meta.get('end'))
        sucursales = json.loads(response.text)['sucursales']
        for suc in sucursales:
            item = SucursalItem(suc)
            id_sucursal = item['id']
            yield item
            yield scrapy.Request(url=productos_url + '?limit={}&id_sucursal={}'.format(LIMIT, id_sucursal),
                                 callback=self.parse_productos_first_page,
                                 headers=HEADERS, meta={'id_sucursal': id_sucursal})

    def parse_productos_first_page(self, response):
        json_data = json.loads(response.text)
        total = json_data['total']
        self.parse_productos_y_precios(response, total)   # procesar  items de la primera pagina ya solicitada

        for offset in xrange(LIMIT, total, LIMIT):
            yield scrapy.Request(url=productos_url + '?limit=50&offset={}&id_sucursal={}'.format(
                offset, response.meta['id_sucursal']),
                                 callback=self.parse_productos_y_precios,
                                 headers=HEADERS,
                                 meta={
                                    'offset': offset,
                                    'total': total,
                                    'id_sucursal': response.meta['id_sucursal']
                                }
                                )

    def parse_productos_y_precios(self, response, total=None):
        json_data = json.loads(response.text)
        self.logger.info('Obteniendo  %s/%s precios para la sucursal %s',
                          response.meta.get('offset', 50),
                          response.meta.get('total', total),
                          response.meta.get('id_sucursal'))
        self.parse_sucursal(response)
        try:
            productos = json_data['productos']
        except KeyError:
            # loggeo el body del response para debugging
            self.logger.error(response.text)
            raise

        items = []
        for prod in productos:
            precio = prod.pop('precio')
            producto = ProductoItem(prod)
            items.append(producto)
            items.append(PrecioItem(precio=precio,
                                    sucursal_id=response.meta['id_sucursal'],
                                    producto_id=producto['id'],
                                    fecha_relevamiento=datetime.utcnow()
                                    )
            )
        return items
