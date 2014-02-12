# -*- coding: utf-8 -*-

"""
fast and dirty scrapping para cargar datos de
sucursales de supermercados de argentina
"""

import json
import urllib
from pprint import pprint
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


    def clean_city(text):

        text = text.replace('GBA', '').replace('Bs As', '').replace('Mendoza', '')
        text = text.replace('-', '').strip()
        d = {'Cabildo': u'Núñez', 'Constituyentes': 'Villa Urquiza',
             'DOT  Baires': 'Saavedra', u'Nogoyá': 'Villa del Parque',
              u'Ramón Falcón': 'Flores', 'Supermercado Caballito': 'Caballito',
              u'Supermercado Honorio Pueyrredón': 'Caballito',
              u'Córdoba Sur': u'Córdoba', u'Córdoba Av. Colón': u'Córdoba',
              u'Córdoba Barrio Talleres': u'Córdoba', 'Comodoro Norte': 'Comodoro Rivadavia',
              u'Tucumán': u'San Miguel de Tucumán', 'Resistencia  Chaco': 'Resistencia',
              'Santa Fe': 'Santa Fe de la Vera Cruz'
            }
        return list(City.objects.filter(name=d.get(text, text)))[-1]

    def parse_info(url):
        pq = PyQuery(url)
        ciudad = clean_city(pq('a.selected').text())

        direccion = re.findall(': (.*)(Aper|Hora)', pq('p#direccion').text())[0][0].strip()
        nombre = pq(pq('p#direccion strong')[0]).text().replace(':', '')
        horarios = re.findall(u'[aA]tención:[ \n\t]+(.*)\.', pq('p#direccion').text(), re.MULTILINE)
        horarios = horarios[0] if len(horarios) else ''
        return Sucursal.objects.create(nombre=nombre,
                                ciudad=ciudad,
                                direccion=direccion,
                                horarios=horarios,
                                cadena=WALMART)



    WALMART = Cadena.objects.get(id=1)

    urls = [
    '/sucursales/cabildo.php',
    '/sucursales/constituyentes.php',
     '/sucursales/saavedra.php',
     '/sucursales/nogoya.php',
     '/sucursales/ramon_falcon.php',
     '/sucursales/supermercado_alberdi_caballito.php',
     '/sucursales/supermercado_honorio_pueyrredon.php',

    '/sucursales/avellaneda.php',
    '/sucursales/parque_avellaneda.php',
    '/sucursales/san_justo.php',
    '/sucursales/quilmes.php',
    '/sucursales/la_tablada.php',
    '/sucursales/pilar.php',
    '/sucursales/san_fernando.php',


     '/sucursales/la_plata.php',
     '/sucursales/bahia_blanca.php',
     '/sucursales/lujan.php',
     '/sucursales/olavarria.php',
     '/sucursales/laferrere.php',

     '/sucursales/cordoba_talleres.php',
     '/sucursales/cordoba_colon.php',
     '/sucursales/cordoba_sur.php',
     '/sucursales/rio_cuarto.php',

    '/sucursales/mendoza_guaymallen.php',
    '/sucursales/mendoza_las_heras.php',
    '/sucursales/mendoza_palmares.php',

     '/sucursales/comodoro_rivadavia.php',
     '/sucursales/comodoro_norte.php',
     '/sucursales/corrientes.php',
     '/sucursales/mendoza_guaymallen.php',
     '/sucursales/mendoza_las_heras.php',
     '/sucursales/mendoza_palmares.php',


     '/sucursales/neuquen.php',
     '/sucursales/parana.php',
     '/sucursales/san_juan.php',
     '/sucursales/santa_fe.php',
     '/sucursales/san_luis.php',
     '/sucursales/tucuman.php',
     '/sucursales/chaco_resistencia.php']


    for i in urls:
        pprint(parse_info('http://www.walmart.com.ar' + i))


def jumbo():
    JUMBO = Cadena.objects.get(id=4)
    pq = PyQuery('http://www.jumbo.com.ar/sucursales.html')
    def get_city(item):
        c = pq('p.localidad', item).text()

        d = {'Chacras': u'Luján de Cuyo', 'Mendoza': 'Godoy Cruz',
             'Pacheco Novo': 'General Pacheco', 'Quilmes 1': 'Quilmes',
             'Quilmes 2': 'Quilmes', u'San Martín': u'General San Martín',
             'Unicenter': u'Martínez', u'Tucumán': u'Yerba Buena',
             'Acoyte': 'Caballito', 'Almagro': 'Almagro',
             'Av. Santa Fe': 'Palermo', 'Juan B. Justo': 'Flores',
             'Madero Harbour': 'Puerto Madero', 'Parque Brown': 'Villa Lugano',
            'Tronador': 'Villa Urquiza', 'Escobar': u'Belén de Escobar'}
        return list(City.objects.filter(name=d.get(c, c)))[-1]

    def parse(i):
        nombre = pq('p.localidad', i).text()
        ciudad = get_city(i)
        direccion, telefono = pq('p.direccion', i).html().split('<br />')[:2]
        return Sucursal.objects.create(nombre=nombre,
                                ciudad=ciudad,
                                direccion=direccion,
                                horarios="Todos los dias de 9 a 22hs",
                                telefono=telefono,
                                cadena=JUMBO)



    for i in pq('div.itemAcordeon'):
        pprint(parse(i))



def vea():

    def get_city(c):

        d = {'Tafi Viejo': u'Tafí Viejo',
             'San Clemente del Tuyu': 'San Clemente del Tuyú',
             'Libertador General San Martin':  5670,
             'Gualeguaychu': u'Gualeguaychú', 'Moron': u'Morón',
             'Neuquen': 'Neuquén', 'Bahia Blanca': u'Bahía Blanca',
             'Rio tercero': 'Río Tercero', 'Las Heras': 5667,
             'San Ramon de la Nueva Oran': u'San Ramón de la Nueva Orán',
             'Maipu': u'Maipú', 'Lujan': u'Luján', 'Junin': u'Junín',
             'San Miguel de Tucuman': u'San Miguel de Tucumán',
             'Chajari': u'Chajarí', 'Tunuyan': u'Tunuyán',
             'Lujan de Cuyo': u'Luján de Cuyo', 'Concepcion': 5671,
             'Lanus': u'Lanús', 'Villa Maria': 5672, 'San Martin': 2006,
             'Malargue': 2995, 'Capital': 5673, 'San Juan': 5673, 'San Miguel': 5674,
             'Guaymallen': u'Guaymallén', 'Canuelas': u'Cañuelas',
             'Cordoba': u'Córdoba', 'Marcos Juarez': u'Marcos Juárez',
             'Rio Cuarto': u'Río Cuarto', 'Paso de Los Libres': 'Paso de los Libres',
             'Parana': u'Paraná', 'Juan Bautista Alberdi': 1535, 'Yerba Buena': 5669
             }

        c = d.get(c, c)
        if isinstance(c, int):
            c = City.objects.get(id=c)
        else:
            c = City.objects.get(name=c)
        return c

    VEA = Cadena.objects.get(id=5)

    for s in json.load(urllib.urlopen('http://www.supermercadosvea.com.ar/sucursales-obtener.html?provincia_id=X')):
        if s['descripcion_url'] == u'bell-ville-bv-colon-850':
            s['direccion'] = u'Bv Colón 850'
        elif s['descripcion_url'] == u'roca-r22-y-gdorvetirgory':
            s['direccion'] = u'Ruta 22 y Gdor. Vetirgory'


        print(Sucursal.objects.create(nombre=s['descripcion'],
                                       ciudad=get_city(s['vea_localidades_desc']),
                                       direccion=s['direccion'],
                                       horarios=s['horarios'],
                                       telefono=s['telefonos'],
                                       cadena=VEA))


if __name__ == '__main__':
    vea()
