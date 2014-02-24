from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cities_light.models import City
from preciosa.precios.models import Sucursal, Cadena

from preciosa.precios.serializers import (CadenaSerializer, SucursalSerializer,
                                          CitySerializer)


class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass



class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.filter(country__name='Argentina')
    serializer_class = CitySerializer


class CadenaViewSet(CreateListRetrieveViewSet):
    queryset = Cadena.objects.all()
    serializer_class = CadenaSerializer


class SucursalViewSet(CreateListRetrieveViewSet):
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
            sucursales = sucursales.filter(ubicacion__distance_lte=circulo).distance(point).order_by('distance')

        serializer = SucursalSerializer(sucursales, many=True)
        return Response(serializer.data)
