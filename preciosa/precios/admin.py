from django.contrib.gis import admin
from django.contrib.gis.geos import Point

from preciosa.precios.models import Cadena, Sucursal

class SucursalAdmin(admin.OSMGeoAdmin):
    center = Point((-45, -55), srid=4326)
    center.transform(900913)

    default_lat = center.x
    default_lon = center.y
    default_zoom = 3


admin.site.register(Cadena)
admin.site.register(Sucursal, SucursalAdmin)
