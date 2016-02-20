# -*- coding: utf-8 -*-
import uuid
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.utils import IntegrityError
from annoying.functions import get_object_or_None
from rest_framework import status, viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from cities_light.models import City
from preciosa.precios.models import (Sucursal, Cadena, Producto,
                                     EmpresaFabricante, Marca, Categoria, Precio)
from preciosa.acuerdos.models import PrecioEnAcuerdo
from preciosa.api.models import MovilInfo
from preciosa.api.serializers import (CadenaSerializer, SucursalSerializer,
                                      CitySerializer, ProductoSerializer,
                                      EmpresaFabricanteSerializer, MarcaSerializer,
                                      CategoriaSerializer, PrecioSerializer,
                                      ProductoDetalleSerializer, UserSerializer,
                                      ProductoDetalleCoorSerializer)
from tools import texto
from tools import gis
import logging
logger = logging.getLogger('main')


class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):

    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    permission_classes = (IsAuthenticated,)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = super(CityViewSet, self).get_queryset()
        q = self.request.query_params.get('q', None)
        if q:
            q = texto.normalizar(q).replace(' ', '')
            queryset = queryset.filter(search_names__startswith=q)[:6]
        return queryset


class CadenaViewSet(CreateListRetrieveViewSet):
    queryset = Cadena.objects.all().order_by('nombre')
    serializer_class = CadenaSerializer


class EmpresaFabricanteViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = EmpresaFabricante.objects.all()
    serializer_class = EmpresaFabricanteSerializer


class MarcaViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class SucursalesList(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):

    permission_classes = (IsAuthenticated,)
    queryset = Sucursal.objects.filter(online=False)
    serializer_class = SucursalSerializer

    def get_queryset(self):
        queryset = super(SucursalesList, self).get_queryset()

        q = self.request.query_params.get('q', None)
        limite = self.request.query_params.get('limite', None)

        lat = self.request.query_params.get('lat', None)
        lon = self.request.query_params.get('lon', None)
        radio = self.request.query_params.get('radio', None)

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
            serializer = SucursalSerializer(sucursal, context={'request': request})
            return Response(serializer.data)
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if data.get('cadena', None) == 'otra':
            data.pop('cadena')

        UBICACION_AUTO = False
        if data.get('ubicacion', None) == 'auto':
            UBICACION_AUTO = data.pop('ubicacion')

        serializer = self.get_serializer(data=data) #, files=request.FILES)

        if serializer.is_valid():
            self.object = serializer.save()
            if UBICACION_AUTO:
                geo = gis.geocode(serializer.instance.ciudad, serializer.instance.direccion)
                ubicacion = Point(geo['lon'], geo['lat'])
                self.object = serializer.save(ubicacion=ubicacion)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductosList(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):

    permission_classes = (IsAuthenticated,)
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_queryset(self):
        pk = self.request.query_params.get('pk', None)  # pk para producto
        q = self.request.query_params.get('q', None)
        limite = self.request.query_params.get('limite', None)

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

    permission_classes = (IsAuthenticated,)
    queryset = Precio.objects.all()
    serializer_class = PrecioSerializer

    def get_queryset(self):
        queryset = super(PreciosList, self).get_queryset()
        producto_id = self.request.query_params.get('producto_id', None)
        sucursal_id = self.request.query_params.get('sucursal_id', None)

        producto = get_object_or_404(Producto, pk=producto_id)
        sucursal = get_object_or_404(Sucursal, pk=sucursal_id)

        queryset = Precio.objects.mas_probables(producto, sucursal)

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class Detalle(object):
    def __init__(self, producto, sucursal, dias, radio):
        self.producto = producto
        self.sucursal = sucursal
        self.dias = dias
        self.radio = radio

    @property
    def similares(self):
        return self.producto.similares()

    @property
    def mas_probables(self):
        probables = Precio.objects.mas_probables(self.producto,
                                                 self.sucursal, dias=self.dias)
        return probables

    @property
    def mejores(self):
        if self.sucursal.ubicacion:
            mejores = Precio.objects.mejores(self.producto,
                                             punto_o_sucursal=self.sucursal,
                                             radio=self.radio, dias=self.dias)
        else:
            mejores = Precio.objects.mejores(self.producto, radio=self.radio,
                                             ciudad=self.sucursal.ciudad,
                                             dias=self.dias)
        return mejores

    @property
    def en_acuerdo(self):
        return PrecioEnAcuerdo.objects.en_acuerdo(self.producto,
                                                  self.sucursal)

class DetalleCoor(object):
    def __init__(self, producto, lat, lng, dias, radio):
        self.producto = producto
        self.dias = dias
        self.radio = radio
        self.lat = float(lat)
        self.lng = float(lng)

    @property
    def similares(self):
        return self.producto.similares()

    @property
    def mejores(self):
        mejores = Precio.objects.mejores(self.producto,
                                         punto_o_sucursal=Point(self.lng, self.lat),
                                         radio=self.radio, dias=self.dias)
        return mejores


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def producto_sucursal_detalle(request, pk_sucursal, pk_producto):
    producto = get_object_or_404(Producto, id=pk_producto)
    sucursal = get_object_or_404(Sucursal, id=pk_sucursal)
    radio = int(request.GET.get('radio', 15))
    dias = int(request.GET.get('dias', 30))
    detalle = Detalle(producto, sucursal, dias, radio)

    def precio_valido(nuevo_precio):
        try:
            nuevo_precio = float(nuevo_precio)
        except ValueError:
            return False

        if nuevo_precio <= 0:
            return False

        if detalle.mas_probables:
            original = float(detalle.mas_probables[0].precio)
            delta = abs(original - float(nuevo_precio)) / original
            if delta > 0.5:
                # si es un 50% mas caro o barato que lo que estaba,
                # ignoramos
                return False

        return True

    if request.method == 'GET':
        serializer = ProductoDetalleSerializer(detalle, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        precio = request.data.get('precio', 0)
        created = request.data.get('created', None)

        if not precio_valido(precio):
            return Response({'detail': 'no aceptado'})

        kwargs = {}
        if created:
            kwargs['created'] = created

        Precio.objects.create(sucursal=sucursal,
                              producto=producto,
                              usuario=request.user,
                              precio=precio, **kwargs)

    return Response({'detail': '¡gracias!'})


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def producto_detalle(request, pk_producto):
    producto = get_object_or_404(Producto, id=pk_producto)
    radio = int(request.GET.get('radio', 15))
    dias = int(request.GET.get('dias', 30))
    lat = request.GET.get('lat', None)
    lng = request.GET.get('lng', None)
    if lat and lng and request.method == 'GET':
        detalle = DetalleCoor(producto, lat, lng, dias, radio)
        serializer = ProductoDetalleCoorSerializer(detalle, context={'request': request})
        return Response(serializer.data)

    return Response({'detail': 'Erroral obtener la información'})



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

       Con un token dado, DRF automáticamente loguea a un usuario (via TokenAuth)
       que queda en request.user
    """
    user = None
    VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
    VALID_MOVIL_INFO_FIELDS = [f.name for f in MovilInfo._meta.fields]
    serialized = UserSerializer(data=request.data, context={'request': request})
    user_data = {field: data for (field, data) in request.data.items()
                 if field in VALID_USER_FIELDS}
    logger.debug("user_data: " + repr(user_data))

    if request.user.is_authenticated() and user_data and serialized.is_valid():
        # el usuario existía pero se envian datos validos. actualizamos datos
        user = request.user
        for attribute, value in user_data.items():
            if attribute == 'password':
                user.set_password(value)
            else:
                setattr(user, attribute, value)
        user.save()
        status_ = status.HTTP_202_ACCEPTED

    elif request.user.is_authenticated() and not user_data:
        # el usuario existía. no hay datos. no se actualiza nada
        user = request.user
        status_ = status.HTTP_200_OK

    elif not request.user.is_authenticated() and user_data and serialized.is_valid():
        # es un registro nuevo con username y password,
        # lo creamos con los datos enviados
        user = get_user_model().objects.create_user(**user_data)
        status_ = status.HTTP_201_CREATED

    elif user_data and not serialized.is_valid():
        # se envia una data errorena. no se actualiza ni se crea un user
        raise exceptions.AuthenticationFailed(serialized.errors)

    elif 'uuid' in request.data and request.data['uuid']:
        # tratamos de conseguir el usuario via un uuid enviado
        movil_user = get_object_or_None(MovilInfo, uuid=request.data['uuid'])

        if movil_user:
            user = movil_user.user
            status_ = status.HTTP_200_OK

    if not user:
        # no se encontró usuario, creamos unos con username random
        username = uuid.uuid4().get_hex()[:30]
        user = get_user_model().objects.create(username=username)
        status_ = status.HTTP_201_CREATED

    assert user

    if 'uuid' in request.data and request.data['uuid']:
        # intentamos asociar la info del movil al usuario

        try:
            movil_info = {field: data for (field, data) in request.data.items()
                          if field in VALID_MOVIL_INFO_FIELDS}
            movil_info['user'] = user
            with transaction.atomic():
                MovilInfo.objects.create(**movil_info)
        except IntegrityError:
            # ya existe este uuid para otro user?
            pass

    token = user.auth_token.key
    return Response({'token': token}, status=status_)


@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def donde_queda(request):
    """dado parámetros lat y lon en decimal,
    devuelve una direccion y ciudad inferida"""

    cualca = {}
    cualca.update(request.data)
    cualca.update(request.query_params)

    if 'lat' not in cualca or 'lon' not in cualca:
        raise exceptions.APIException('lat y lon son obligatorios')
    lon, lat = cualca['lon'][0], cualca['lat'][0]
    queda = gis.donde_queda(lat, lon)
    queda['ciudad_nombre'] = unicode(queda['ciudad']).replace(', Argentina', '')
    queda['ciudad'] = queda['ciudad'].id
    return Response(queda)
