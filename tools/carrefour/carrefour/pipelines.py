# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem

from preciosa.precios.models import Cadena, Sucursal
from cities_light.models import City

class CarrefourPipeline(object):

    ids = []
    cadenas = {
            u'Carrefour hiper': Cadena.objects.filter(nombre='Carrefour'),
            u'Carrefour market': Cadena.objects.filter(nombre='Carrefour Market'),
            u'Carrefour express': Cadena.objects.filter(nombre='Carrefour Express'),
            u'Carrefour maxi': Cadena.objects.filter(nombre='Carrefour Maxi'),
            }

    def process_item(self, item, spider):
        if item['nombre'] in ids:
            raise DropItem('Sucursal ya en archivo %s' % item['nombre'])
        if suc['tipo'] not in cadenas.values():
            raise DropItem('Sucursal tipo %s desconocida. No insertando %s' % (item['tipo'], item['nombre']))

        prov_ciudad = item['direccion'].split(',')[1].split()
        provincia = ''
        ciudad = None
        for e in reversed(prov_ciudad):
            provincia = '%s %s' % (e, provincia)
            cities = City.objects.filter(name=provincia)
            if cities.count() == 1:
                ciudad = cities[0]

        if ciudad is None:
            raise DropItem('Sucursal %s no posee dirección conocida %s' % (item['nombre'], item['direccion']))

        sucursal = Sucursal(nombre=item['nombre'], direccion=item['direccion'].split(',')[0], telefono=item['telefono'])
        sucursal.cadena = cadenas[item['tipo']]
        sucursal.city = ciudad
        return item
