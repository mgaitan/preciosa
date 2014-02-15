from django import forms

from preciosa.voluntarios.models import MapaCategoria


class MapaCategoriaForm(forms.ModelForm):
    class Meta:
        model = MapaCategoria
        widgets = {
            'origen': forms.HiddenInput(),
        }

