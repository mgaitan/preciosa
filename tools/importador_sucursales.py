# -*- coding: utf-8 -*-

"""
fast and dirty scrapping para cargar datos de
sucursales de supermercados de argentina
"""

import re
from django.db import IntegrityError
from django.db.models import Q
from pyquery import PyQuery
from cities_light.models import City
from preciosa.precios.models import Cadena, Sucursal


class smart_dict(dict):
    def __missing__(self, key):
        return key


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def buscar_ciudad(ciudad, default='Buenos Aires'):
    try:
        ciudad = City.objects.get(Q(name__iexact=ciudad) | Q(name_ascii__iexact=ciudad))
    except City.DoesNotExist:
        try:
            ciudad = City.objects.get(alternate_names__icontains=ciudad)
        except City.DoesNotExist:
            ciudad = City.objects.get(name='Buenos Aires')
    return ciudad


def import_coto():
    URL = 'http://www.coto.com.ar/mapassucursales/Sucursales/ListadoSucursales.aspx'
    COTO = Cadena.objects.get(nombre='Coto')
    HOR_TMPL = "Lunes a Jueves: %s\nViernes: %s\nSábado: %s\nDomingo: %s"

    normalize_ciudad = smart_dict({'CAP. FED.': 'Capital Federal',
                                   'VTE LOPEZ': 'Vicente Lopez',
                                   'CAPITAL': 'Capital Federal',
                                   'CAP.FED': 'Capital Federal',
                                   'CAP.FEDERAL': 'Capital Federal',
                                   'MALVINAS ARGENTINAS': 'Los Polvorines',
                                   'CDAD. DE BS.AS': 'Capital Federal',
                                   'V ILLA LUGANO': 'Villa Lugano',
                                   'CIUDAD DE SANTA FE': 'Santa Fe',
                                   'CUIDAD DE SANTA FE': 'Santa Fe',
                                   'FISHERTON': 'Rosario',
                                   'GRAL MADARIAGA': 'General Juan Madariaga',
                                   'PARUQUE CHACABUCO': 'Parque Chacabuco',
                                   '': 'Mataderos'
                                   })

    pq = PyQuery(URL)
    for row in pq('table.tipoSuc tr'):
        suc = pq(row)
        if not 'verDetalle' in suc.html():
            continue
        nombre = suc.children('td').eq(2).text().title()
        horarios = HOR_TMPL % tuple([t.text for t in suc.children('td')[3:7]])

        direccion = suc.children('td').eq(7).text().split('-')
        ciudad = buscar_ciudad(normalize_ciudad[direccion[-1].strip()])
        direccion = '-'.join(direccion[:-1]).strip().title()
        telefono = suc.children('td').eq(8).text().strip()
        print Sucursal.objects.create(nombre=nombre, ciudad=ciudad, direccion=direccion,
                                      horarios=horarios, telefono=telefono, cadena=COTO)


def importador_laanonima(url_id=None, start=1):
    """
    >>> importador_laanonima()
    ...
    157 La Anónima (Dirección:Hector Gil n° 64)
    158 La Anónima ()
    Revisar: [119, 123, 134, 136, 137, 138, 139, 140, 147, 148, 150, 151,
              152, 153, 154, 155, 156, 157]

    >>> Cadena.objects.all()[7].sucursales.all().count()
    132
    """

    patron1 = re.compile(r'(?P<suc>Suc.*\: )?(?P<dir>.*),?.*\((?P<cp>\d+)\), (?P<ciu>.*),?(?P<prov> .*)?$')
    patron2 = re.compile(r'(Suc.*\: )?(.*), (.*), (.*)$')
    URL_BASE = 'http://www.laanonima.com.ar/sucursales/sucursal.php?id='
    LA_ANONIMA = Cadena.objects.get(nombre=u"La Anónima")
    normalize_ciudad = {156: 'Perito Moreno', 153: 'Río Colorado'}


    def scrap(url_id):
        revisar = False
        url = URL_BASE + str(url_id)
        pq = PyQuery(url)
        nombre = pq('td.titulos').eq(0).text().strip()
        if not nombre:
            return
        descripcion = pq('td.descipciones').eq(1).text()
        if any(k in descripcion.lower() for k in ['quick', 'transferencia']):
            return
        try:
            horarios = re.search(r'atenci\xf3n: (.*) [\xc1A]rea', descripcion).groups()[0]
        except (AttributeError, IndexError):
            horarios = ''
        direccion = pq('td.descipciones').eq(2).text()

        try:
            _, direccion, cp, ciudad, provincia = patron1.match(direccion).groups()
        except (TypeError, AttributeError):
            try:
                _, direccion, ciudad, provincia = patron2.match(direccion).groups()
                cp = None
            except (TypeError, AttributeError):
                cp = None
                direccion = direccion.split(',')[0]
                ciudad = normalize_ciudad.get(int(url_id), 'Río Gallegos')     # default
                revisar = True
        direccion = direccion.strip().replace('í a ', 'ía ')    # common fix
        if direccion and direccion[-1] == ',':
            direccion = direccion[:-1]

        ciudad = buscar_ciudad(ciudad.strip(), 'Río Gallegos')

        telefono = pq('td.descipciones').eq(3).text()
        try:
            print url_id, Sucursal.objects.create(nombre=nombre, ciudad=ciudad, direccion=direccion,
                                   horarios=horarios, telefono=telefono, cadena=LA_ANONIMA,
                                   cp=cp)
        except IntegrityError as e:
            print 'Fallo en ', url
            print '    ', e
            revisar = True
        return revisar

    if url_id:
        scrap(url_id)
    else:
        revisar = []
        for i in range(start, 159):
            if scrap(i):
                revisar.append(i)
        print "Revisar:", revisar


def walmart():
	"""importador de walmart"""

    def parse_info(url):
        pq = PyQuery(url)
        nombre = pq('p#direccion').text().split(':')[1]
        direccion = pq(pq('p#direccion strong')[0]).text().replace(':', '').capitalize()





    WALMART = Cadena.objects.get(id=1)
    pq = PyQuery('http://www.walmart.com.ar/sucursales/cabildo.php')

    for i in pq('ol#sucursalessidemenu li'):



    Sucursal.objects.create(nombre=nombre,
                            ciudad=ciudad,
                            direccion=direccion,
                            horarios=horarios,
                            telefono=telefono,
                            cadena=WALMART,
                                   cp=cp)





if __name__ == '__main__':
    importador_walmart()
