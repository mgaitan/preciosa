import re
from django.contrib.gis.geos import Point
from rest_framework import serializers
from cities_light.models import City

from preciosa.precios.models import (Cadena, Sucursal, Producto, Categoria,
                                     EmpresaFabricante, Marca, Precio)


class CategoriaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Categoria


class EmpresaFabricanteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmpresaFabricante
        fields = ('id', 'url', 'nombre')


class MarcaSerializer(serializers.HyperlinkedModelSerializer):
    fabricante = EmpresaFabricanteSerializer()

    class Meta:
        model = Marca
        fields = ('id', 'url', 'nombre', 'fabricante')


class CadenaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cadena
        fields = ('id', 'url', 'nombre','cadena_madre',)


class UbicacionField(serializers.WritableField):
    def to_native(self, obj):
        return "%s" % obj

    def from_native(self, data):
        try:
            lon, lat = map(float, re.findall(r'(-?\d+\.\d*)', data))
            return Point(lon, lat)
        except ValueError:
            pass


class SucursalSerializer(serializers.ModelSerializer):
    cadena = CadenaSerializer(source='cadena')
    ubicacion = UbicacionField(required=False)

    class Meta:
        model = Sucursal
        fields = (
            'id',
            'cadena',
            'nombre',
            'ubicacion',
            'ciudad',
            'direccion',
            'horarios',
            'telefono'
        )



class ProductoSerializer(serializers.HyperlinkedModelSerializer):

    foto = serializers.CharField(source='foto_abs', required=False)

    class Meta:
        model = Producto
        fields = (
            'id',
            'descripcion',
            'marca',
            'upc',
            'foto',
        )


class CitySerializer(serializers.HyperlinkedModelSerializer):
    region = serializers.Field(source='region.name')

    class Meta:
        model = City
        fields = ('name','latitude','longitude','geoname_id','region')


class PrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precio
        fields = (
            'producto',
            'sucursal',
            'precio'
        )
