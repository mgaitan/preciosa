from rest_framework import serializers
from cities_light.models import City
from preciosa.precios.models import (Cadena, Sucursal, Producto, Categoria,
                                     EmpresaFabricante, Marca)


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


class SucursalSerializer(serializers.HyperlinkedModelSerializer):
    lat = serializers.Field()
    lon = serializers.Field()

    class Meta:
        model = Sucursal
        fields = (
            'id',
            'cadena',
            'nombre',
            'lat',
            'lon',
            'ciudad',
            'direccion',
            'horarios',
            'telefono'
        )


class ProductoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Producto
        fields = (
            'descripcion',
            'marca',
            'upc',
        )


class CitySerializer(serializers.HyperlinkedModelSerializer):
    region = serializers.Field(source='region.name')

    class Meta:
        model = City
        fields = ('name','latitude','longitude','geoname_id','region')
