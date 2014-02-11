
from django.shortcuts import get_object_or_404
from django.views.generic import ListView


from preciosa.precios.models import Cadena, Sucursal, Producto, Categoria
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
