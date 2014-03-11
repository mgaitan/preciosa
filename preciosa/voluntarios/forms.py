# -*- coding: utf-8 -*-
import autocomplete_light
import floppyforms as forms

from cities_light.models import City
from preciosa.precios.models import (Categoria, Cadena, EmpresaFabricante,
                                     Marca, Sucursal)
from preciosa.voluntarios.models import MapaCategoria
from preciosa.voluntarios.mixins import CleanNombreMixin


class PointWidget(forms.gis.PointWidget, forms.gis.BaseGMapWidget):
    map_width = 500
    map_height = 350


class MapaCategoriaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MapaCategoriaForm, self).__init__(*args, **kwargs)
        self.fields['origen'].queryset = Categoria.por_clasificar()
        self.fields[
            'comentario'].help_text = u'Por favor, indicá las categorías que usarías'

    class Meta:
        model = MapaCategoria
        widgets = {
            'origen': forms.HiddenInput(),
        }


class MarcaModelForm(forms.ModelForm, CleanNombreMixin):

    # flag para que el mixin distinga que modelform es
    model_related = Marca

    qs = EmpresaFabricante.objects.all().order_by('nombre')
    # en el form lo hacemos obligatorio
    fabricante = forms.ModelChoiceField(queryset=qs,
                                        help_text='Por favor, revisá bien este campo.')

    class Meta:
        model = Marca
        exclude = ['logo', 'logo_cropped']
        help_texts = {
            'nombre': 'Tiene que ser una marca nueva. '
                      'Si la que querés agregar aparece en la lista, '
                      'quiere decir que ya la conocemos.',
        }


class LogoMarcaModelForm(forms.ModelForm):

    """form para subir/editar el logo de una marca"""
    class Meta:
        model = Marca
        fields = ['logo', 'logo_cropped']


class EmpresaFabricanteModelForm(forms.ModelForm, CleanNombreMixin):
    model_related = EmpresaFabricante

    class Meta:
        model = EmpresaFabricante
        fields = ['nombre']
        help_texts = {
            'nombre': 'Tiene que ser una empresa nueva.'
        }


class CadenaModelForm(forms.ModelForm, CleanNombreMixin):
    model_related = Cadena
    cadena_madre = forms.ModelChoiceField(Cadena.objects.all(),
                                          label=u'Pertenece a', required=False,
                                          help_text=u'Por ejemplo, Jumbo y Vea son de Cencosud')   # noqa

    class Meta:
        model = Cadena
        fields = ['cadena_madre', 'nombre']


class SucursalModelForm(forms.ModelForm, CleanNombreMixin):
    model_related = Sucursal
    max_cantidad_palabras = 4
    max_largo = 30
    puede_ser_vacio = True

    ciudad = forms.ModelChoiceField(
        City.objects.all(), widget=autocomplete_light.ChoiceWidget('CityAutocomplete'))

    ubicacion = forms.gis.PointField(widget=PointWidget, required=False)

    class Meta:
        model = Sucursal
        fields = ('cadena', 'nombre', 'ciudad', 'direccion', 'ubicacion', 'cp',
                  'telefono', 'horarios')
