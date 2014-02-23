from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from preciosa.precios.models import Sucursal
from preciosa.precios.serializers import SucursalSerializer

@api_view(['GET',])
def sucursales_list(request):
    if request.method == 'GET':
        sucursales = Sucursal.objects.all()

        if request.GET.get('l'):
            point_str = [float(p) for p in request.GET.get('l').split('|')]
            point = Point(*point_str, srid=4326)
            distance = request.GET.get('d', 5)

            sucursales = sucursales.filter(ubicacion__distance_lte=(point, D(km=distance)))


        serializer = SucursalSerializer(sucursales, many=True)
        return Response(serializer.data)
