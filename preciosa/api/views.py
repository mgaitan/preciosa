from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q

from rest_framework import viewsets, mixins, generics

from cities_light.models import City
from preciosa.precios.models import Sucursal, Cadena, Producto

from preciosa.precios.serializers import (CadenaSerializer, SucursalSerializer,
                                          CitySerializer, ProductoSerializer)


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

        q = self.request.QUERY_PARAMS.get('q', None)

        lat = self.request.QUERY_PARAMS.get('lat', None)
        lon = self.request.QUERY_PARAMS.get('lon', None)
        radio = self.request.QUERY_PARAMS.get('radio', None)

        if q:
            queryset = queryset.filter(Q(cadena__nombre__icontains=q) | Q(nombre__icontains=q))

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


class ProductosList(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):

    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_queryset(self):
        queryset = super(ProductosList, self).get_queryset()
        barcode = self.request.QUERY_PARAMS.get('barcode', None)
        string = self.request.QUERY_PARAMS.get('string', None)

        if barcode:
            queryset = queryset.filter(upc__icontains=barcode)

        if string:
            queryset = queryset.filter(
                Q(descripcion__icontains=string)
                #| Q(marca__nombre__icontains=string)
                #| Q(marca__fabricante__nombre__icontains=string)
            )

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
