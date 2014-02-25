# coding=utf-8
import re

from django import forms
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class AuthenticatedViewMixin(object):
    """Mixin para vistas que requieren autenticación"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AuthenticatedViewMixin, self).dispatch(*args, **kwargs)


class CleanNombreMixin(object):

    max_cantidad_palabras = 3
    max_largo = 20
    max_palabras_con_numeros = 1
    model_related = None

    def clean_nombre(self):
        """algunos controles sobre el input del usuario,
        para protegernos todo lo posible de info basura

        """
        kind = self.model_related._meta.verbose_name

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
        if len(nombre) > self.max_largo:
            raise forms.ValidationError(u"¿No es un nombre de %s demasiado largo? "
                                        u"Envianos un mensaje si estamos equivocados" % kind)    # noqa

        # si tiene mas de 3 palabras, es sospechoso
        # '9 de Oro'
        if len(palabras) > self.max_cantidad_palabras:
            raise forms.ValidationError(u"¿No son demasiadas palabras para una %s? "
                                        u"Envianos un mensaje si estamos equivocados" % kind)    # noqa

        # si las palabras no son palabras o numeros, también.
        if not all(map(lambda a: re.search(r'^[a-z0-9áéíóúüñ]+$', a.encode('utf8'), flags=re.UNICODE), palabras)):
            raise forms.ValidationError(u"No parece una %s ¿Estás usando algún caracter extraño? "  # noqa
                                        u"Envianos un mensaje si estamos equivocados" % kind)     # noqa
        #si hay más de una palabra que sea de numeros, also
        if count_int(palabras) > self.max_palabras_con_numeros:
            raise forms.ValidationError(u"¿No demasiados números en esta %s? "
                                        u"Envianos un mensaje si estamos equivocados" % kind)     # noqa
        nombre = capitalizar(palabras)
        # Model = Marca if kind == 'marca' else EmpresaFabricante
        if self.model_related.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError(u"¿Seguro que esta %s no existe ya? "
                                        u"Envianos un mensaje si estamos equivocados" % kind)    # noqa
        return nombre
