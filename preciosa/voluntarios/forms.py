from django import forms

from preciosa.precios.models import (Categoria, Marca,
                                     EmpresaFabricante, Cadena)
from preciosa.voluntarios.models import MapaCategoria

from image_cropping import ImageCropWidget


class MapaCategoriaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MapaCategoriaForm, self).__init__(*args, **kwargs)
        self.fields['origen'].queryset = Categoria.por_clasificar()

    class Meta:
        model = MapaCategoria
        widgets = {
            'origen': forms.HiddenInput(),
        }



class LogoMarcaModelForm(forms.ModelForm):
    """este es el primer form que se le muestra al user para que suba una imagen"""
    class Meta:
        model = Marca
        fields = ['logo', 'logo_cropped']


class EmpresaFabricanteModelForm(forms.ModelForm):
    class Meta:
        model = EmpresaFabricante


class CadenaModelForm(forms.ModelForm):
    class Meta:
        model = Cadena
