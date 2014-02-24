from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from rest_framework import viewsets, mixins, generics

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
    serializer_class = SucursalSerializer


class SucursalesList(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):

    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer

    def get_queryset(self):
        queryset = super(SucursalesList, self).get_queryset()
        lat = self.request.QUERY_PARAMS.get('lat', None)
        lon = self.request.QUERY_PARAMS.get('lon', None)
        radio = self.request.QUERY_PARAMS.get('radio', None)
        if all((lat, lon, radio)):
            try:
                lat = float(lat)
                lon = float(lon)
                radio = float(radio)
            except ValueError:
                pass
            else:
                point = Point(lon, lat, srid=4326)
                circulo = (point, D(km=radio))
                queryset = queryset.filter(ubicacion__distance_lte=circulo)
                queryset = queryset.distance(point).order_by('distance')
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
