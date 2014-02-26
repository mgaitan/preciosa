# -*- coding: utf-8 -*-
import re
from django import forms

from preciosa.precios.models import (Categoria, Marca,
                                     EmpresaFabricante, Cadena)
from preciosa.voluntarios.models import MapaCategoria


class MapaCategoriaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MapaCategoriaForm, self).__init__(*args, **kwargs)
        self.fields['origen'].queryset = Categoria.por_clasificar()
        self.fields['comentario'].help_text = u'Por favor, indicá las categorías que usarías'

    class Meta:
        model = MapaCategoria
        widgets = {
            'origen': forms.HiddenInput(),
        }


class CleanNombreMixin(object):

    def clean_nombre(self):
        """algunos controles sobre el input del usuario,
        para protegernos todo lo posible de info basura

        """
        kind = self.kind

        def count_int(palabras):
            # why the hell no a regex? because they sucks
            c = 0
            for p in palabras:
                try:
                    int(p)
                    c += 1
                except ValueError:
                    pass
            return c

        def capitalizar(palabras):
            """('la', 'morenita') ->  La Morenita
               ('0', 'de', 'ORO') -> 9 de Oro
            """
            result = []
            for i, palabra in enumerate(palabras):
                if i == 0 or len(palabra) > 2:
                    result.append(palabra.capitalize())
                else:
                    result.append(palabra)
            return ' '.join(result)

        data = self.cleaned_data
        nombre = data['nombre'].lower().strip()
        palabras = nombre.split()

        # marca muy larga?
        if len(nombre) > 20:
            raise forms.ValidationError("¿No es un nombre de %s demasiado largo?"
                                        "Envianos un mensaje si estamos equivocados" % kind)    # noqa


        # si tiene mas de 3 palabras, es sospechoso
        # '9 de Oro'
        if len(palabras) > 3:
            raise forms.ValidationError("¿No son demasiadas palabras para una %s?"
                                        "Envianos un mensaje si estamos equivocados" % kind)    # noqa

        # si las palabras no son palabras o numeros, también.
        if not all(map(lambda a: re.search(r'^[a-z0-9áéíóúüñ]+$', a.encode('utf8'), flags=re.UNICODE), palabras)):
            raise forms.ValidationError("No parece una %s ¿Estás usando algún caracter extraño?" # noqa
                                        "Envianos un mensaje si estamos equivocados" % kind)     # noqa
        #si hay más de una palabra que sea de numeros, also
        if count_int(palabras) > 1:
            raise forms.ValidationError("¿No demasiados números en esta %s?"
                                        "Envianos un mensaje si estamos equivocados" % kind)     # noqa
        nombre = capitalizar(palabras)
        Model = Marca if kind == 'marca' else EmpresaFabricante
        if Model.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("¿Seguro que esta %s no existe ya?"
                                        "Envianos un mensaje si estamos equivocados" % kind)    # noqa
        return nombre



class MarcaModelForm(forms.ModelForm, CleanNombreMixin):

    kind = 'marca'      # flag para que el mixin distinga que modelform es

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
    kind = 'empresa'

    class Meta:
        model = EmpresaFabricante
        fields = ['nombre']
        help_texts = {
            'nombre': 'Tiene que ser una empresa nueva.'
        }



class CadenaModelForm(forms.ModelForm):
    class Meta:
        model = Cadena
