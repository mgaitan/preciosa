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
from cities_light.models import City
from preciosa.precios.models import Cadena, Sucursal

class SucursalSpider(Spider):
	"""Hace scrapping de las sucursales de Carrefour"""
	name = "sucursales"
	allowed_domains = ['carrefour.com.ar']
	start_urls = ['http://www.carrefour.com.ar/storelocator/index/']

	def parse(self, response):
		reqs = []
		for city in City.objects.all():
			reqs.append( (city.search_names, ','.join([unicode(city.latitude), unicode(city.longitude)]) ) ) 
		forms = []
		for city,geocode in reqs:
			forms.append(FormRequest.from_response(response, formdata={'search[address]': city, "search[type]":"address", "search[geocode]": geocode, "country":"AR"},
			callback=self.after_submit, formxpath="//form[@id='storelocator_search_form']"))
		return forms

	def after_submit(self, response):
		print PROJECT_ROOT
		pq = PyQuery(response.body_as_unicode())
		items = []
		for result in pq('div.storelocator_result'):
			nodes = result.findall('div')
			suc = SucursalItem()
			suc['nombre'] = nodes[0].getchildren()[0].text
			# suc.type = nodes[1].getchildren()[0].attrib['title']
			suc['direccion'] = ', '.join([nodes[2].text, nodes[3].text])
			suc['telefono'] = nodes[4].text.strip()
			items.append(suc)

		return items
		