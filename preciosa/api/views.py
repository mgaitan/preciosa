# -*- coding: utf-8 -*-
import uuid
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from annoying.functions import get_object_or_None
from rest_framework import status, viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from cities_light.models import City
from preciosa.precios.models import (Sucursal, Cadena, Producto,
                                     EmpresaFabricante, Marca, Categoria, Precio)

from preciosa.api.models import MovilInfo
from preciosa.api.serializers import (CadenaSerializer, SucursalSerializer,
                                      CitySerializer, ProductoSerializer,
                                      EmpresaFabricanteSerializer, MarcaSerializer,
                                      CategoriaSerializer, PrecioSerializer,
                                      ProductoDetalleSerializer, UserSerializer)


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
            queryset = queryset.buscar(q)

        if all((lat, lon, radio)):
            try:
                lat = float(lat)
                lon = float(lon)
                radio = float(radio)
            except ValueError:
                pass
            else:
                queryset = queryset.alrededor_de(Point(lon, lat), radio)

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
    def similares(self):
        return self._producto.similares()

    @property
    def sucursal(self):
        return self._sucursal

    @property
    def mas_probables(self):
        probables = Precio.objects.mas_probables(self._producto,
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


@api_view(['POST'])
def registro(request):
    """esta vista crea o actualiza un usuario.
       Devuelve el token unico, creado con la señal post_save de User.
       que cada post debe enviar como header Authorization

       Tambien actualiza crea o actualiza
       una instancia de MovilInfo asociada al usuario si se envia un uuid.

       por ejemplo, via jquery::

            $.ajaxSetup({
              headers: {
                'Authorization': "Token XXXXX"
              }
            });

       Con un token dado, DRF automáticamente loguea a un usuario
       que queda en request.user
    """
    user = None
    user_data = {}
    VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
    VALID_MOVIL_INFO_FIELDS = [f.name for f in MovilInfo._meta.fields]
    serialized = UserSerializer(data=request.DATA)
    if serialized.is_valid():
        user_data = {field: data for (field, data) in request.DATA.items()
                     if field in VALID_USER_FIELDS}

    if request.user.is_authenticated() and user_data:
        # el usuario existía. actualizamos datos
        user = request.user
        for attribute, value in user_data.items():
            if attribute == 'password':
                user.set_password(value)
            else:
                setattr(user, value)
        user.save()
        status_ = status.HTTP_202_ACCEPTED

    elif request.user.is_authenticated() and not user_data:
        # el usuario existía. no se actualiza nada
        user = request.user
        status_ = status.HTTP_200_OK

    elif not request.user.is_authenticated() and user_data:
        # es un registro nuevo con username y password,
        # lo creamos con los datos enviados
        user = get_user_model().objects.create_user(**user_data)
        status_ = status.HTTP_201_CREATED

    elif 'uuid' in request.DATA:
        # tratamos de conseguir el usuario via un uuid enviado
        user = get_object_or_None(MovilInfo, uuid=request.DATA['uuid'])
        status_ = status.HTTP_200_OK

    if not user:
        # no se encontró usuario, creamos unos con username random
        username = uuid.uuid4().get_hex()
        user = get_user_model.objects.create(username=username)
        status_ = status.HTTP_201_CREATED

    assert user

    if 'uuid' in request.DATA:
        # intentamos asociar la info del movil al usuario
        try:
            movil_info = {field: data for (field, data) in request.DATA.items()
                          if field in VALID_MOVIL_INFO_FIELDS}
            movil_info['user'] = user
            MovilInfo.objects.create(**movil_info)
        except IntegrityError:
            # ya existe este uuid para otro user?
            pass

    token = user.auth_token.key
    return Response({'token': token}, status=status_)
