# -*- coding: utf-8 -*-
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from preciosa.voluntarios.models import MapaCategoria
from preciosa.voluntarios.forms import MapaCategoriaForm


MSG_EXITO = [u'Buenísimo, Guardamos tu elección ¿Otra?',
             u'¡Gracias! Era el dato que nos faltaba ¿Seguís con una más?',
             u'Muy buena elección, ya nos faltan menos ¿Qué te parece esta?',
             u'¡Claro, cómo no se nos ocurrió! ¿Qué eligirías para este caso?',
             u'¡Sospechábamos eso! Gracias por confirmarlo. ¿Podés seguir con otra?',
             u'¡Muy bien! ¿Ves? Muchas manos en un plato no siempre hacen garabatos. ¿Otra?']


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

    # necesitamos saber qué origines ya usó el User
    ya_hechas = [v.origen.id for v in MapaCategoria.objects.filter(user=request.user)]

    try:
        origen = MapaCategoria.CAT_ORIGEN.exclude(id__in=ya_hechas).order_by('?')[0]
    except MapaCategoria.DoesNotExist:

        messages.success(request, u"¡Categorizaste todo! "
                                  u"Increíble tu ayuda, muchas gracias")
        return redirect('voluntarios_dashboard')

    form.initial['origen'] = origen.id
    productos_ejemplo = origen.producto_set.all()[:4]

    return render(request, 'voluntarios/mapa_categorias.html',
                  {'form': form, 'origen': origen,
                   'productos_ejemplo': productos_ejemplo})


