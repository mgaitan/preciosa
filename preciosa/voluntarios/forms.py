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


class MarcaModelForm(forms.ModelForm):
    class Meta:
        model = Marca


class EmpresaFabricanteModelForm(forms.ModelForm):
    class Meta:
        model = EmpresaFabricante


class CadenaModelForm(forms.ModelForm):
    class Meta:
        model = Cadena
