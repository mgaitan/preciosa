# -*- coding: utf-8 -*-
import random
from django.db.models.loading import get_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from annoying.decorators import ajax_request
from annoying.functions import get_object_or_None
from cities_light.models import City
from preciosa.precios.models import Categoria, Marca, Sucursal
from preciosa.voluntarios.mixins import AuthenticatedViewMixin
from preciosa.voluntarios.models import (MapaCategoria, MarcaEmpresaCreada,
                                         SucursalCadenaCreada)
from preciosa.voluntarios.forms import (
    CadenaModelForm, EmpresaFabricanteModelForm,
    MapaCategoriaForm, MarcaModelForm,
    LogoMarcaModelForm, SucursalModelForm)
from tools.gis import get_geocode_data


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
    productos_ejemplo = origen.productos.all().order_by('?')[:4]

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
            field = 'empresa'
        else:
            form = form_marca = MarcaModelForm(request.POST)
            txt = 'la marca'
            field = 'marca'

        if form.is_valid():
            instance = form.save()
            d = {'user': request.user, field: instance}
            MarcaEmpresaCreada.objects.create(**d)
            messages.success(request,
                             u'¡Genial! Guardamos %s %s' % (txt, instance.nombre))
            return redirect('alta_marca')

    creados = MarcaEmpresaCreada.objects.exclude(
        user=request.user).order_by('created')[:5]

    return render(request, 'voluntarios/alta_marca.html', {'creados': creados,
                  'form_marca': form_marca, 'form_empresa': form_empresa})


@login_required
@ajax_request
def voto_item(request, pk):
    if request.method == 'POST':
        # Utilizo get_model para que este método sea común a varios modelos
        app_label, model_name = request.POST.get('model', '.').split(".")
        model = get_model(app_label, model_name)
        item = get_object_or_404(model, pk=pk)
        if item.votos.filter(user=request.user).exists():
            # el user ya votó este item
            return {'result': False}
        voto = 1 if request.POST.get('voto') == 'true' else -1
        # el trackeo de los votos, se debe hacer sobre un entidad llamada
        # "Voto[nombre_entidad]. Ej: MarcaEmpresaCreada y
        # VotoMarcaEmpresaCreada
        get_model(app_label, u"Voto{}".format(model_name)).objects.create(
            user=request.user, item=item, voto=voto)
        return {'result': True}
    return {'result': False}


def autocomplete_nombre_marca(request):
    q = request.GET.get('q', '')
    context = {'q': q}
    queries = {}
    queries['marcas'] = Marca.objects.filter(nombre__icontains=q)[:6]

    context.update(queries)
    return render(request, "voluntarios/autocomplete_nombre_marca.html",
                  context)


def autocomplete_nombre_sucursal(request):
    q = request.GET.get('q', '')
    context = {'q': q}
    queries = {}
    queries['sucursales'] = Sucursal.objects.filter(nombre__icontains=q)[:6]

    context.update(queries)
    return render(request, "voluntarios/autocomplete_nombre_sucursal.html",
                  context)


class AltaCadenaSucursalesView(AuthenticatedViewMixin, CreateView):
    template_name = "voluntarios/alta_cadena_sucursal.html"
    form_class = SucursalModelForm
    second_form_class = CadenaModelForm

    def get_context_data(self, **kwargs):
        context = super(AltaCadenaSucursalesView,
                        self).get_context_data(**kwargs)
        if 'form_sucursal' not in context:
            context['form_sucursal'] = self.form_class()
        if 'form_cadena' not in context:
            context['form_cadena'] = self.second_form_class()
        context["creados"] = SucursalCadenaCreada.objects.exclude(
            user=self.request.user).order_by('created')[:5]
        return context

    def form_invalid(self, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):

        if 'btn_form_sucursal' in request.POST:
            form_class = self.get_form_class()
            form_name = 'form_sucursal'
        else:
            form_class = self.second_form_class
            form_name = 'form_cadena'

        self.object = None
        form = self.get_form(form_class)

        if form.is_valid():
            instance = form.save()
            scCreada = {'user': request.user,
                        form_name.split('_')[1]: instance}
            SucursalCadenaCreada.objects.create(**scCreada)
            return self.form_valid(form)
        else:
            return self.form_invalid(**{form_name: form})

    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.SUCCESS,
                             u"¡Excelente! Guardamos la {} {}".format(
                                 self.object._meta.verbose_name,
                                 self.object))
        return reverse('alta_cadena_sucursal')

alta_cadena_sucursal = AltaCadenaSucursalesView.as_view()


@ajax_request
def geo_code_data(request):
    if request.method == 'GET':
        ciudad = get_object_or_None(City, id=request.GET.get('ciudad', None))
        direccion = request.GET.get('direccion', None)
        return get_geocode_data(ciudad, direccion)
