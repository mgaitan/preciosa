# -*- coding: utf-8 -*-
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from cities_light.models import City
from preciosa.precios.models import (Sucursal, Cadena, Producto,
                                     EmpresaFabricante, Marca, Categoria, Precio)

from preciosa.api.serializers import (CadenaSerializer, SucursalSerializer,
                                      CitySerializer, ProductoSerializer,
                                      EmpresaFabricanteSerializer, MarcaSerializer,
                                      CategoriaSerializer, PrecioSerializer,
                                      ProductoDetalleSerializer)


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


class EmpresaFabricanteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmpresaFabricante.objects.all()
    serializer_class = EmpresaFabricanteSerializer


class MarcaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class SucursalesList(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):

    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer

    def get_queryset(self):
        queryset = super(SucursalesList, self).get_queryset()

        q = self.request.QUERY_PARAMS.get('q', None)
        limite = self.request.QUERY_PARAMS.get('limite', None)

        lat = self.request.QUERY_PARAMS.get('lat', None)
        lon = self.request.QUERY_PARAMS.get('lon', None)
        radio = self.request.QUERY_PARAMS.get('radio', None)

        if q:
            queryset = queryset.filter(Q(cadena__nombre__icontains=q) |
                                       Q(nombre__icontains=q))

        if all((lat, lon, radio)):

            # TODO: refactor para generalizar esto con el codigo
            # de Sucursal.cercanas()
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

        if limite:
            queryset = queryset[:limite]

        return queryset

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            sucursal = self.get_object()
            serializer = SucursalSerializer(sucursal)
            return Response(serializer.data)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductosList(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):

    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_queryset(self):
        pk = self.request.QUERY_PARAMS.get('pk', None)  # pk para producto
        q = self.request.QUERY_PARAMS.get('q', None)
        limite = self.request.QUERY_PARAMS.get('limite', None)

        queryset = super(ProductosList, self).get_queryset()

        if pk:
            queryset = queryset.filter(pk=pk)
        elif q:
            queryset = Producto.objects.buscar(q, limite)

        if hasattr(self, '_pk_sucursal'):
            queryset = queryset.filter(precios__sucursal__id=self._pk_sucursal).distinct()

        return queryset

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            self._pk_sucursal = kwargs['pk']
        return self.list(request, *args, **kwargs)


class PreciosList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):

    queryset = Precio.objects.all()
    serializer_class = PrecioSerializer

    def get_queryset(self):
        queryset = super(PreciosList, self).get_queryset()
        producto_id = self.request.QUERY_PARAMS.get('producto_id', None)
        sucursal_id = self.request.QUERY_PARAMS.get('sucursal_id', None)

        producto = get_object_or_404(Producto, pk=producto_id)
        sucursal = get_object_or_404(Sucursal, pk=sucursal_id)

        queryset = Precio.objects.mas_probables(producto, sucursal)

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class Detalle(object):
    def __init__(self, producto, sucursal):
        self._producto = producto
        self._sucursal = sucursal

    @property
    def producto(self):
        return self._producto

    @property
    def sucursal(self):
        return self._sucursal

    @property
    def mas_probables(self):
        probables =  Precio.objects.mas_probables(self._producto,
                                            self._sucursal, dias=30)
        return probables


    @property
    def mejores(self):
        if self._sucursal.ubicacion:
            mejores = Precio.objects.mejores(self._producto,
                                                     punto_o_sucursal=self._sucursal,
                                                     radio=20, dias=30)
        else:
            mejores = Precio.objects.mejores(self._producto,
                                                     ciudad=self._sucursal.ciudad,
                                                     dias=30)
        return mejores


@api_view(['GET', 'POST'])
def producto_sucursal_detalle(request, pk_sucursal, pk_producto):
    producto = get_object_or_404(Producto, id=pk_producto)
    sucursal = get_object_or_404(Sucursal, id=pk_sucursal)
    detalle = Detalle(producto, sucursal)

    if request.method == 'GET':
        serializer = ProductoDetalleSerializer(detalle)
        return Response(serializer.data)
    elif request.method == 'POST':
        # a futuro el POST requirá un token según issue #201
        # para encontrar el user
        # token = request.QUERY_PARAMS.get('token', None)
        # user = get_or_None(User, usertokens__token=token)
        precio = request.DATA.get('precio', None)
        created = request.DATA.get('created', None)
        if precio:
            kwargs = {}
            if created:
                kwargs['created'] = created
            Precio.objects.create(sucursal=sucursal, producto=producto,
                                  precio=precio, **kwargs)
        return Response({'detail': '¡gracias!'})





