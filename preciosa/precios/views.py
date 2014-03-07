
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import HttpResponse
from preciosa.precios.models import Producto, Categoria
import operator

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
    if len(q) < 3:
        return HttpResponse('')

    context = {'q': q}
    try:
        int(q)
        es_num = True
    except ValueError:
        es_num = False

    if es_num:
        productos = Producto.objects.filter(upc__startswith=q)[0:8]
    else:
        words = q.split(' ')

        palabras = Q(reduce(operator.and_,
                            (Q(descripcion__icontains=w) for w in words if len(w) > 2)))
        tiene_palabras = Producto.objects.filter(
            palabras).values_list('id', flat=True)
        similares = Producto.objects.filter_o(
            descripcion__similar=q).values_list('id',
                                                flat=True)
        productos = Producto.objects.filter(Q(id__in=tiene_palabras) |
                                            Q(id__in=similares)).distinct()[0:8]
    context['productos'] = productos

    return render(request, "precios/autocomplete.html", context)
