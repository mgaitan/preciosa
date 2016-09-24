import re
from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model
from rest_framework import serializers
from cities_light.models import City

from preciosa.precios.models import (Cadena, Sucursal, Producto, Categoria,
                                     EmpresaFabricante, Marca, Precio)
from preciosa.acuerdos.models import PrecioEnAcuerdo


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()


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
        fields = ('id', 'url', 'nombre', 'cadena_madre',)


class UbicacionField(serializers.Field):
    def to_representation(self, obj):
        return "%s" % obj

    def to_internal_value(self, data):
        try:
            lon, lat = map(float, re.findall(r'(-?\d+\.\d*)', data))
            return Point(lon, lat)
        except ValueError:
            pass


class SucursalSerializer(serializers.ModelSerializer):
    cadena_completa = CadenaSerializer(source='cadena', read_only=True)
    ubicacion = UbicacionField(required=False)
    ciudad_nombre = serializers.CharField(source='ciudad', read_only=True)
    ciudad_provincia = serializers.CharField(source='ciudad', read_only=True)

    def transform_ciudad_nombre(self, obj, value):
        return obj.ciudad.name

    def transform_ciudad_provincia(self, obj, value):
        return obj.ciudad.region.name

    class Meta:
        model = Sucursal
        fields = (
            'id',
            'cadena',
            'nombre',
            'ubicacion',
            'ciudad',
            'ciudad_nombre',
            'ciudad_provincia',
            'cadena_completa',
            'direccion',
            'horarios',
            'telefono'
        )


class RelatedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = (
            'id',
            'descripcion',
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


class PrecioSerializer(serializers.ModelSerializer):
    sucursal = SucursalSerializer()
    acuerdos = serializers.SerializerMethodField()

    def get_acuerdos(self, foo):
        return PrecioEnAcuerdo.objects.en_acuerdo(foo.producto, foo.sucursal)

    class Meta:
        model = Precio
        fields = (
            'producto',
            'sucursal',
            'created',
            'precio',
            'acuerdos'
        )


class EnAcuerdoSerializer(serializers.Serializer):
    nombre = serializers.CharField(source='acuerdo__nombre', read_only=True)
    precio = serializers.DecimalField(read_only=True, max_digits=8, decimal_places=2)


class ProductoDetalleSerializer(serializers.Serializer):
    producto = ProductoSerializer()
    sucursal = SucursalSerializer()
    mas_probables = PrecioSerializer(many=True, partial=True)
    en_acuerdo = EnAcuerdoSerializer(many=True, partial=True)
    mejores = PrecioSerializer(many=True, partial=True)
    similares = RelatedProductSerializer(many=True, partial=True)


class ProductoDetalleCoorSerializer(serializers.Serializer):
    producto = ProductoSerializer()
    mejores = PrecioSerializer(many=True, partial=True)
    similares = RelatedProductSerializer(many=True, partial=True)


class CitySerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='name', read_only=True)

    def transform_name(self, obj, value=''):
        return unicode(obj).replace(', Argentina', '')

    class Meta:
        model = City
        fields = ('id', 'name', 'latitude', 'longitude', 'geoname_id')
