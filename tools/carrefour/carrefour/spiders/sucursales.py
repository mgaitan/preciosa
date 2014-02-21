import os, sys
sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../../../') ) )
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "preciosa.settings")

from pyquery import PyQuery
from scrapy.spider import Spider
from scrapy.http import FormRequest
from scrapy.selector import Selector

from carrefour.items import SucursalItem

from django.db import IntegrityError
from django.db.models import Q
from cities_light.models import City, Region
from preciosa.precios.models import Cadena, Sucursal

class SucursalSpider(Spider):
	"""Hace scrapping de las sucursales de Carrefour"""
	name = "sucursales"
	allowed_domains = ['carrefour.com.ar']
	start_urls = ['http://www.carrefour.com.ar/storelocator/index/']

	def parse(self, response):
		reqs = []
		forms = []
		for region in Region.objects.filter(country__name='Argentina'):
			for city in region.city_set.filter(population__gt=1000):
				forms.append( FormRequest.from_response(response, formdata={'search[address]': city.display_name, "search[type]":"address",
						"search[geocode]": ','.join([unicode(city.latitude), unicode(city.longitude)]), "country":"AR"},
						callback=self.after_submit, formxpath="//form[@id='storelocator_search_form']") )
		return forms

	def after_submit(self, response):
		pq = PyQuery(response.body_as_unicode())
		items = []
		for result in pq('div.storelocator_result'):
			nodes = result.findall('div')
			suc = SucursalItem()
			suc['nombre'] = nodes[0].getchildren()[0].text
			suc['tipo'] = nodes[1].getchildren()[0].attrib['title']
			suc['direccion'] = ', '.join([nodes[2].text, nodes[3].text])
			suc['telefono'] = nodes[4].text.strip()
			items.append(suc)

		return items
		