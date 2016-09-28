# -*- coding: utf-8 -*-
import scrapy


class SucursalItem(scrapy.Item):
    
    sucursalTipo = scrapy.Field()
    direccion = scrapy.Field()
    provincia = scrapy.Field()
    banderaId = scrapy.Field()
    localidad = scrapy.Field()
    banderaDescripcion = scrapy.Field()
    comercioRazonSocial = scrapy.Field()
    lat = scrapy.Field()
    lng = scrapy.Field()
    sucursalNombre = scrapy.Field()
    comercioId = scrapy.Field()
    id = scrapy.Field()
    sucursalId = scrapy.Field()


class ProductoItem(scrapy.Item):
	nombre = scrapy.Field()
	presentacion = scrapy.Field()
	marca = scrapy.Field()
	id = scrapy.Field()


class PrecioItem(scrapy.Item):
	sucursal_id = scrapy.Field() 
	producto_id = scrapy.Field()
	precio = scrapy.Field()
	fecha_relevamiento = scrapy.Field(serializer=str)