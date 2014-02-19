# -*- coding: utf-8 -*-
from django import forms

from preciosa.precios.models import (Categoria, Marca,
                                     EmpresaFabricante, Cadena)
from preciosa.voluntarios.models import MapaCategoria


class MapaCategoriaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MapaCategoriaForm, self).__init__(*args, **kwargs)
        self.fields['origen'].queryset = Categoria.por_clasificar()

    class Meta:
        model = MapaCategoria
        widgets = {
            'origen': forms.HiddenInput(),
        }


class MarcaModelForm(forms.ModelForm):
    qs = EmpresaFabricante.objects.all()
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


class EmpresaFabricanteModelForm(forms.ModelForm):
    class Meta:
        model = EmpresaFabricante
        fields = ['nombre']
        help_texts = {
            'nombre': 'Tiene que ser una empresa nueva.'
        }


class CadenaModelForm(forms.ModelForm):
    class Meta:
        model = Cadena
