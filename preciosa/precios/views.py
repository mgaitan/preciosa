from preciosa.precios.models import Cadena, Sucursal
from cities_light.models import City

from rest_framework import viewsets
from preciosa.precios.serializers import (CadenaSerializer, SucursalSerializer,
                                          CitySerializer)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CadenaViewSet(viewsets.ModelViewSet):
    queryset = Cadena.objects.all()
    serializer_class = CadenaSerializer


class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer   # Create your views here.
