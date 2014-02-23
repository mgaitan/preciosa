from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cities_light.models import City
from preciosa.precios.models import Sucursal, Cadena

from preciosa.precios.serializers import (CadenaSerializer, SucursalSerializer,
                                          CitySerializer)

# API


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class CadenaViewSet(viewsets.ModelViewSet):
    queryset = Cadena.objects.all()
    serializer_class = CadenaSerializer


class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer   # Create your views here.


@api_view(['GET'])
def sucursales_list(request):
    if request.method == 'GET':
        sucursales = Sucursal.objects.all()

        if request.GET.get('l'):
            point_str = [float(p) for p in request.GET.get('l').split('|')]
            point = Point(*point_str, srid=4326)
            distance = request.GET.get('d', 5)
            circulo = (point, D(km=distance))
            sucursales = sucursales.filter(ubicacion__distance_lte=circulo)

        serializer = SucursalSerializer(sucursales, many=True)
        return Response(serializer.data)
