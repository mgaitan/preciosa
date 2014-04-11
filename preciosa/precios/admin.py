from django.contrib.gis import admin
from django.contrib.gis.geos import Point
from preciosa.precios.models import (Cadena, Sucursal, Marca,
                                     EmpresaFabricante, Producto,
                                     DescripcionAlternativa, Categoria)
from image_cropping import ImageCroppingMixin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory


class CategoriaAdmin(TreeAdmin):
    form = movenodeform_factory(Categoria)
    list_filter = ['depth']
    search_fields = ['nombre']


class MarcaAdmin(ImageCroppingMixin, admin.ModelAdmin):
    search_fields = ['nombre', 'fabricante__nombre']


class FabricanteAdmin(ImageCroppingMixin, admin.ModelAdmin):
    search_fields = ['nombre']


class CadenaAdmin(ImageCroppingMixin, admin.ModelAdmin):
    search_fields = ['nombre', 'cadena_madre__nombre']


class ProductoAdmin(admin.ModelAdmin):
    search_fields = ['descripcion', 'marca__nombre', 'UPC']


class DescripcionAlternativaAdmin(admin.ModelAdmin):
    search_fields = ['descripcion', 'marca__nombre', 'UPC']


class SucursalAdmin(admin.OSMGeoAdmin):
    center = Point((-45, -55), srid=4326)
    center.transform(900913)
    default_lat = center.x
    default_lon = center.y
    default_zoom = 3

    list_fields = ['cadena']
    list_filter = ['cadena']
    search_fields = ['busqueda']


admin.site.register(Marca, MarcaAdmin)
admin.site.register(EmpresaFabricante, FabricanteAdmin)
admin.site.register(Cadena, CadenaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(DescripcionAlternativa, DescripcionAlternativaAdmin)
admin.site.register(Sucursal, SucursalAdmin)
admin.site.register(Categoria, CategoriaAdmin)
