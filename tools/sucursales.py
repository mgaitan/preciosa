# -*- coding: utf-8 -*-
"""
funciones comunes para scrappers de sucursales
"""


from tools import texto

from preciosa.precios.models import Cadena
from cities_light.models import City, Region


PROVINCIAS = [texto.normalizar(prov.name) for prov in Region.objects.all()]


def inferir_cadena(nombre, return_object=False):
    """si el nombre de una y sólo una cadena está en
    el nombre de la sucursal devolvemos esa cadena y su id"""

    cadenas = [(texto.normalizar(cadena), cadena, id)
               for (cadena, id) in Cadena.objects.extra(select={'length':'Length(nombre)'}).order_by('-length').values_list('nombre', 'id')]

    result = None
    for cadena_normal, cadena, id in cadenas:
        if cadena_normal in texto.normalizar(nombre):
            if result is None:
                result = Cadena.objects.get(id=id) if return_object else (cadena, id)
            else:
                return None
    return result


def inferir_ciudad(ciudad, provincia=None, estricto=False, return_object=False):
    nombreciudad = texto.normalizar(ciudad.replace(' ', ''))
    # ejemplo "Pto. Madryn"
    if '.' in nombreciudad:
        nombreciudad = nombreciudad.split('.')[1]
    buscar = "%sargentina" % nombreciudad
    kwargs = {}
    if isinstance(provincia, int):
        kwargs['region__id'] = provincia

    try:
        ciudad = City.objects.get(name__iexact=ciudad, **kwargs)
    except (City.DoesNotExist, City.MultipleObjectsReturned):
        try:
            ciudad = City.objects.get(search_names__icontains=buscar, **kwargs)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            ciudad = None

    if ciudad and not estricto:
        return (ciudad.name, ciudad.region.name, ciudad.id) if not return_object else ciudad

    elif provincia:
        if isinstance(provincia, int):
            provincia = Region.objects.get(id=provincia).name

        nombreprov = texto.normalizar(provincia.replace(' ', ''))
        buscar = "%s%sargentina" % (nombreciudad, nombreprov)
        try:
            ciudad = City.objects.get(search_names__istartswith=buscar)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            ciudad = None

        if ciudad:
            return ciudad.name, ciudad.region.name, ciudad.id if not return_object else ciudad
