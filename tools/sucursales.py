# -*- coding: utf-8 -*-
"""
funciones comunes para scrappers de sucursales
"""


from tools import texto

from preciosa.precios.models import Cadena
from cities_light.models import City, Region


PROVINCIAS = [texto.normalizar(prov.name) for prov in Region.objects.all()]
CADENAS = [(texto.normalizar(cadena), cadena, id)
           for (cadena, id) in Cadena.objects.all().values_list('nombre', 'id')]


def inferir_cadena(nombre):
    """si el nombre de una y sólo una cadena está en
    el nombre de la sucursal devolvemos esa cadena y su id"""
    result = None
    for cadena_normal, cadena, id in CADENAS:
        if cadena_normal in texto.normalizar(nombre):
            if result is None:
                result = cadena, id
            else:
                return None
    return result


def inferir_ciudad(ciudad, provincia=None, estricto=False):
    nombreciudad = texto.normalizar(ciudad.replace(' ', ''))
    # ejemplo "Pto. Madryn"
    if '.' in nombreciudad:
        nombreciudad = nombreciudad.split('.')[1]
    buscar = "%sargentina" % nombreciudad
    try:
        ciudad = City.objects.get(search_names__icontains=buscar)
    except (City.DoesNotExist, City.MultipleObjectsReturned):
        ciudad = None

    if ciudad and not estricto:
        return ciudad.name, ciudad.region.name, ciudad.id
    elif provincia:
        nombreprov = texto.normalizar(provincia.replace(' ', ''))
        buscar = "%s%sargentina" % (nombreciudad, nombreprov)
        try:
            ciudad = City.objects.get(search_names__istartswith=buscar)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            ciudad = None

        if ciudad:
            return ciudad.name, ciudad.region.name, ciudad.id