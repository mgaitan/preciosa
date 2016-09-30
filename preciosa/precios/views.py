# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from preciosa.precios.models import Producto, Categoria

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
        context['active'] = ','.join(['li.cat-%d a:first' % p.id
                                      for p in self.categoria.get_ancestors()])
        return context


class ProductoDetailView(DetailView):

    model = Producto

    context_object_name = "producto"
    template_name = "precios/detalle_producto.html"

    def get_context_data(self, **kwargs):

        context = super(ProductoDetailView, self).get_context_data(**kwargs)
        context['precios'] = self.object.precios.order_by('created')[:8]
        # Add in the publisher
        context['active'] = ','.join(['li.cat-%d a:first' % p.id
                                      for p in self.object.categoria.get_ancestors()])
        context['prods_similares'] = self.object.similares()
        return context


class ProductosSearchAutocomplete(ListView):
    model = Producto

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        if not q or len(q) < 3:
            return Producto.objects.none()
        qs = Producto.objects.buscar(q)[:8]
        return qs

    def get(self, request, *args, **kwargs):
        data = {
            'results': [{
                'id': result.id,
                'value': result.descripcion,
                'url': result.get_absolute_url()
            } for result in self.get_queryset()
            ]
        }
        return JsonResponse(data)
