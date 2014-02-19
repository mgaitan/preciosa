# -*- coding: utf-8 -*-
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from preciosa.precios.models import Categoria, Marca
from preciosa.voluntarios.models import MapaCategoria
from preciosa.voluntarios.forms import (MapaCategoriaForm,
                                        MarcaModelForm,
                                        EmpresaFabricanteModelForm,
                                        LogoMarcaModelForm)


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


@login_required
def logos(request, pk=None, paso=None):
    if pk is None:
        # selecciono una marca al azar y
        try:
            instance = Marca.objects.filter(logo='').order_by('?')[0]
        except Marca.DoesNotExist:
            messages.success(request, u"¡No quedan marcas sin logo!")
            return redirect('voluntarios_dashboard')
        return redirect('logos_marca', pk=instance.id, paso=1)

    instance = get_object_or_404(Marca, id=pk)

    # paso 1 o 2. Si ya subimos, luego recortamos
    form = LogoMarcaModelForm(instance=instance)

    if request.method == "POST":
        form = LogoMarcaModelForm(request.POST, request.FILES,
                                  instance=instance)

        if form.is_valid():
            instance = form.save()
            if paso == '2':
                # ya es es el segundo paso, vamos a otros
                messages.success(request,
                                 u"¡Gracias! Ahora %s tiene logo" % instance.nombre)
                return redirect('logos')
            else:
                messages.info(request, u"Ahora recortá la imágen que subiste")
                return redirect('logos_marca', pk=instance.id, paso=2)

    return render(request, 'voluntarios/logos.html',
                  {'form': form, 'instance': instance,
                   'paso': paso})


@login_required
def alta_marca(request, pk=None, paso=None):

    instance = get_object_or_404(Marca, id=pk) if pk else None

    form_marca = MarcaModelForm()
    form_empresa = EmpresaFabricanteModelForm()

    if request.method == "POST":

        es_empresa = request.POST.get('es_empresa')
        if es_empresa:
            form = form_empresa = EmpresaFabricanteModelForm(request.POST)
            txt = 'el fabricante'
        else:
            form = form_marca = MarcaModelForm(request.POST)
            txt = 'la marca'

        if form.is_valid():
            instance = form.save()
            import ipdb; ipdb.set_trace()
            messages.success(request,
                             u'¡Genial! Guardamos %s %s' % (txt, instance.nombre))
            return redirect('alta_marca')

    return render(request, 'voluntarios/alta_marca.html',
                  {'form_marca': form_marca, 'form_empresa': form_empresa})


def autocomplete_nombre_marca(request):
    q = request.GET.get('q', '')
    context = {'q': q}
    queries = {}
    queries['marcas'] = Marca.objects.filter(nombre__icontains=q)[:6]

    context.update(queries)
    return render(request, "voluntarios/autocomplete_nombre_marca.html",
                  context)
