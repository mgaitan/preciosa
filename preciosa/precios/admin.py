from django.contrib.gis import admin
from django.contrib.gis.geos import Point
from preciosa.precios.models import (Cadena, Sucursal, Marca,
                                     EmpresaFabricante, Producto,
                                     Categoria)
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory


class CategoriaAdmin(TreeAdmin):
    form = movenodeform_factory(Categoria)


class SucursalAdmin(admin.OSMGeoAdmin):
    center = Point((-45, -55), srid=4326)
    center.transform(900913)

    default_lat = center.x
    default_lon = center.y
    default_zoom = 3


admin.site.register(Marca)
admin.site.register(EmpresaFabricante)
admin.site.register(Cadena)
admin.site.register(Producto)
admin.site.register(Sucursal, SucursalAdmin)
admin.site.register(Categoria, CategoriaAdmin)
