
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.db.models import Q

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
        # Add in the publisher
        context['active'] = ','.join(['li.cat-%d a:first' % p.id
                                      for p in self.object.categoria.get_ancestors()])
        return context


def autocomplete_buscador(request):
    q = request.GET.get('q', '')
    context = {'q': q}
    queries = {}
    queries['productos'] = Producto.objects.filter(
        Q(descripcion__icontains=q) |
        Q(upc__startswith=q)).distinct()[:6]

    context.update(queries)

    return render(request, "precios/autocomplete.html", context)
