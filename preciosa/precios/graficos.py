# -*- coding: utf-8 -*-
from preciosa.precios.models import Precio, Sucursal, Producto
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext
from django.utils import simplejson as json
from preciosa.precios.tests.factories import (SucursalFactory,
                                              ProductoFactory,
                                              PrecioFactory)
from datetime import time, date, timedelta

"""
    Genera objetos json con datos formateados para ser
    graficados por la libraría de gráficos .js
    Flot
"""

IDS_SUCURSALES_ONLINE = []

IDS_SUCURSALES = IDS_SUCURSALES_ONLINE

def to_flottimestamp(dt):
    """Converts a datetime object to UTC timestamp"""
    return  int(dt.strftime("%s"))*1000


# genera el json con los datos para graficar en flot
def graphdata_sucursal(sucursal, producto, dias=30):
    data = list(Precio.objects.historico(sucursal=sucursal, producto=producto,
                                        dias=dias, distintos=False))

    points = []
    for item in data:
        fecha, precio = item['created'], item['precio']
        points.append([to_flottimestamp(fecha), float(precio)])

    graph_data = {"data": points, "label": sucursal.nombre}

    return graph_data


# hacer un grafico comparando todas las sucursales online
def graphdata_comparando_sucursales(producto, dias=30):
    sucursales = Sucursal.objects.filter(online=True)
    graph_data = [graphdata_sucursal(s, producto, dias) for s in sucursales]

    return graph_data
    

# hacer un grafico del promedio
def graphdata_promedio_sucursales():
    pass
