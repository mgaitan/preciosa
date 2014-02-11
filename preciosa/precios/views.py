
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView


from preciosa.precios.models import Cadena, Sucursal, Producto, Categoria
from cities_light.models import City

from rest_framework import viewsets
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


# Vistas web

class ProductosListView(ListView):

    context_object_name = "productos"
    template_name = "precios/lista_productos.html"

    def get_queryset(self):
        self.categoria = get_object_or_404(Categoria, id=self.args[0])
        return Producto.objects.filter(categoria=self.categoria)

    def get_context_data(self, **kwargs):
        context = super(ProductosListView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['categoria'] = self.categoria
        context['active'] = ','.join(['li.cat-%d a:first' % p.id for p in self.categoria.get_ancestors()])
        return context


class ProductoDetailView(DetailView):

    model = Producto

    context_object_name = "producto"
    template_name = "precios/detalle_producto.html"


    def get_context_data(self, **kwargs):

        context = super(ProductoDetailView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['active'] = ','.join(['li.cat-%d a:first' % p.id for p in self.object.categoria.get_ancestors()])
        return context
