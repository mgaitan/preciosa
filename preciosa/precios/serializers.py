from rest_framework import serializers
from cities_light.models import City
from preciosa.precios.models import Cadena, Sucursal



class CadenaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cadena
        fields = ('nombre',)


class SucursalSerializer(serializers.HyperlinkedModelSerializer):
    lat = serializers.Field()
    lon = serializers.Field()

    class Meta:
        model = Sucursal
        fields = (
            'cadena',
            'nombre',
            'lat',
            'lon',
            'ciudad',
            'direccion',
            'horarios',
            'telefono'
        )


class CitySerializer(serializers.HyperlinkedModelSerializer):
    region = serializers.Field(source='region.name')

    class Meta:
        model = City
        fields = ('name',)
