# -*- coding: utf-8 -*-
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from preciosa.precios.models import Categoria
from preciosa.voluntarios.models import MapaCategoria
from preciosa.voluntarios.forms import MapaCategoriaForm


MSG_EXITO = [u'Buenísimo, Guardamos tu elección ¿Otra?',
             u'¡Gracias! Era el dato que nos faltaba ¿Seguís con una más?',
             u'Muy buena elección, ya nos faltan menos ¿Qué te parece esta?',
             u'¡Claro, cómo no se nos ocurrió! ¿Qué eligirías para este caso?',
             u'¡Sospechábamos eso! Gracias por confirmarlo. ¿Podés seguir con otra?',
             u'¡Muy bien! ¿Ves? Muchas manos en un plato no siempre hacen garabatos. ¿Otra?']  # noqa


def dashboard(request):
    """una home page para usuarios que quieren colaborar"""
    return render(request, 'voluntarios/dashboard.html', {})


@login_required
def mapa_categorias(request):
    """implementacion del ticket #64"""

    data = request.POST if request.method == 'POST' else None
    form = MapaCategoriaForm(data)
    if form.is_valid():

        voto = form.save(commit=False)
        voto.user = request.user
        voto.save()
        messages.success(request, random.choice(MSG_EXITO))
        return redirect('mapa_categorias')

    # necesitamos saber qué origenes ya usó el User
    try:
        categorizables = MapaCategoria.categorizables_por_voluntario(
            request.user)
    except MapaCategoria.DoesNotExist:

        messages.success(request, u"¡Categorizaste todo! "
                                  u"Increíble tu ayuda, muchas gracias")
        return redirect('voluntarios_dashboard')

    # elegimos una al azar (sólo si no hay errores previos)
    if request.method == 'POST':
        origen = MapaCategoria.categorizables_por_voluntario(
            request.user).get(id=request.POST['origen'])
    else:
        origen = categorizables.order_by('?')[0]
    a_clasificar = Categoria.por_clasificar().count()
    percent = int((a_clasificar - categorizables.count()) * 100 /
                  a_clasificar)



    form.initial['origen'] = origen.id

    # random asi no sesgamos los resultados
    productos_ejemplo = origen.producto_set.all().order_by('?')[:4]

    return render(request, 'voluntarios/mapa_categorias.html',
                  {'form': form, 'origen': origen,
                   'productos_ejemplo': productos_ejemplo,
                   'percent': percent})
