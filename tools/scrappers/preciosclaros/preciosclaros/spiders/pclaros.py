
import urllib
import json
from datetime import datetime
import scrapy
from preciosclaros.items import SucursalItem, ProductoItem, PrecioItem


HEADERS = {'x-api-key': 'qfcNgctUb27Qw5w07u0sA5pNfp51Q9mo9XhIuZpw', 
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.89 Safari/537.36'}

base_url = 'https://8kdx6rx8h4.execute-api.us-east-1.amazonaws.com/' 
sucursales_url = base_url + 'prod/sucursales'     # ?limit=50&offset=50
productos_url = base_url + 'prod/productos'  # ?id_sucursal


class PreciosClarosSpider(scrapy.Spider):
    name = "preciosclaros"

    def start_requests(self):
        yield scrapy.Request(url=sucursales_url + '?limit=50', 
                             callback=self.parse_sucursal_first_page, 
                             headers=HEADERS)

    def parse_sucursal_first_page(self, response):
        json_data = json.loads(response.text)
        total = json_data['total']
        self.parse_sucursal(response)  

        # process pages          
        for offset in xrange(50, total, 50):
            yield scrapy.Request(url=sucursales_url + '?limit=50&offset={}'.format(offset), 
                                 callback=self.parse_sucursal, 
                                 headers=HEADERS, meta={'offset': offset, 'total': total})

    def parse_sucursal(self, response):
        json_data = json.loads(response.text)
        total = json_data['total']
        self.logger.info('Obteniendo %s/%s sucursales', response.meta.get('offset', 50), total)
        sucursales = json.loads(response.text)['sucursales']
        for suc in sucursales:
            item = SucursalItem(suc)
            id_sucursal = item['id']
            yield item 
            yield scrapy.Request(url=productos_url + '?limit=50&id_sucursal={}'.format(id_sucursal), 
                                 callback=self.parse_productos_first_page, 
                                 headers=HEADERS, meta={'id_sucursal': id_sucursal})


    def parse_productos_first_page(self, response):
        json_data = json.loads(response.text)
        total = json_data['total']
        self.parse_productos_y_precios(response)   # procesar  items de la primera pagina ya solicitada

        for offset in xrange(50, total, 50):
            yield scrapy.Request(url=productos_url + '?limit=50&offset={}&id_sucursal={}'.format(
                offset, response.meta['id_sucursal']), 
                                 callback=self.parse_productos_y_precios, 
                                 headers=HEADERS, 
                                 meta={
                                    'offset': offset, 
                                    'total': total, 
                                    'id_sucursal': response.meta['id_sucursal']
                                })
        

    def parse_productos_y_precios(self, response):
        json_data = json.loads(response.text)
        self.logger.info('Obteniendo  %s/%s precios para la sucursal %s', 
                          response.meta.get('offset', 50), 
                          response.meta.get('total', '?'), 
                          response.meta.get('id_sucursal'))
        self.parse_sucursal(response)  
        productos = json_data['productos']
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

