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


class MarcaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Marca
        fields = ('id', 'nombre',)


class CadenaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cadena
        fields = ('id', 'nombre','cadena_madre',)


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
