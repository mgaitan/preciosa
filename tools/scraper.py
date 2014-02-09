# -*- coding: utf-8 -*-

"""
Cada Cadena de supermecados entrega una lista de sucursales. A su vez, cada sucursal es un 
diccionario cuyas claves son: 'nombre' -> Nombre de la sucursal, 'telefono' -> teléfono de 
la sucursal, 'horarios', etc
"""

import urllib
import lxml.html
import json
import pprint


def ciudad_a_ID(ciud, prov):
    """Para buscar ID de ciudad de acuerdo al fixture"""
    with open('../fixtures/ciudades.json') as json_data:
        data = json.load(json_data)
        json_data.close()
        res = [item for item in data if 'search_names' in item['fields'].keys()
                and ciud.lower()+prov.lower() in item['fields']['search_names']]
        pprint(res)

def ID_a_ciudad(numero):
    """Para ver a que ciudad corresponde cierto ID"""
    with open('../fixtures/ciudades.json') as json_data:
        data = json.load(json_data)
        json_data.close()
        res = [item for item in data if item['pk'] == numero]
        pprint(res)


class HiperLibertad:
    """ Clase para scraping de datos del Híper Libertad"""

    base_url = 'https://www.libertadsa.com.ar/misucursal_'
    city_url = {4546: 'cordoba.php',                    #Cordoba
                2896: 'mendoza.php',                    #Mendoza
                2081: 'salta.php',                      #Salta
                5676: 'santafe.php',               #Rosario
                286: 'chaco.php',                       #Resistencia
                409: 'misiones.php',                    #Posadas
                5673: 'sanjuan.php',                    #San Juan
                1999: 'tucuman.php',                    #San Miguel
                1945: 'santiago.php'}                   #Santiago

    def __init__(self):

        self.data = []
        
        # Ordena los datos. Construye una lista de sucursales
        # para la cadena HiperLibertad.
        for city in self.city_url.keys():
            for sucursal in self.get_page_data(city):
                self.data.append(sucursal)

        self.json = json.dumps(self.data)

    def get_page_data(self, city):
        """ Realiza el scraping, de a una url por vez.
        Entrega una lista de sucursales scrapeadas de
        base_url + comp_url. """

        htmlraw = urllib.urlopen(self.base_url + self.city_url[city])
        doc = lxml.html.document_fromstring(htmlraw.read())
        
        #scraping de datos usando xpath.
        sucursales = []
        i = 3  # Para i < 3 no hay datos :(.
        while True:
            sucursales.append( doc.xpath('/html/body/div/div[9]/div[2]/div[2]/p['
                    + str(i) + ']/span/text() | /html/body/div/div[9]/div[2]/div[2]/p['
                    + str(i) + ']/span[2]/span/text()' ) )
            if not sucursales[-1]:
                del sucursales[-1]
                break
            i += 1

        # Formateo de datos: Lista de sucursales. Cada sucursal es un 
        # dict (claves: 'nombre', 'direccion', etc)
        format_datos = []
        for sucursal in sucursales:
            _ = {}
            datos = filter(None, [' '.join(x.split()) for x in sucursal])  # CleanUp de datos 
            _['nombre'] = datos[0]
            _['direccion'] = datos[1]
            _['cp'] = datos[2]
            _['telefono'] = datos[3]
            _['horarios'] = datos[4]
            _['director'] = datos[5]
            _['ciudad'] = city
            format_datos.append(_)
        return format_datos


class Yaguar:
    """ Clase para scraping de datos de la cadena yaguar"""

    base_url = 'http://www.yaguar.com/frontendSP/asp/'
    suc_url = {1157: 'iframe_Autopista.asp',                        #CABA
               2938: 'iframe_sucursalSantaFe.asp',                  #Santa Fe
               286: 'iframe_SucursalesChaco.asp',                   #Resistencia
               2896: 'iframe_SucursalesMendoza.asp',                #Mendoza
               5232: 'iframe_Sucursalesbahiablanca.asp',            #Bahia Blanca
               1143: 'iframe_SucursalesCampana.asp',                #Campana
               5606: 'iframe_SucursalesMoreno.asp',                 #Moreno
               1111111: 'iframe_SucursalesjoseCpaz.asp',            #Jose C Paz
               4546: 'iframe_sucursalescordoba.asp',                #Cordoba
               151: 'iframe_SucursalesTigre.asp',                   #Tigre
               2758: 'iframe_sucursalesneuquen.asp',                #Neuquen
               2081: 'iframe_sucursalesSalta.asp',                  #Salta
               582: 'iframe_MardelPlata.asp',                       #Mar del Plata
               5673: 'iframe_SanJuan.asp'}                          #San Juan

    def __init__(self):

        self.data = []

        # Retornar un listado de sucursales para la cadena yaguar
        for ciudad in self.suc_url.keys():
            self.data.append(self.get_page_data(ciudad))

        self.json = json.dumps(self.data)

    def get_page_data(self, ciudad):
        """ Realiza el scraping de datos para la cadena Yaguar.
        El scraping es de a una url por vez """

        htmlraw = urllib.urlopen(self.base_url + self.suc_url[ciudad])
        doc = lxml.html.document_fromstring(htmlraw.read())

        sucursal = {}
        # Scraping usando xpath
        datos1 = doc.xpath('//*[@class]/text()')  
        datos2 = doc.xpath('//*[@class]/b/text()')

        #CleanUp de datos
        datos1 = [ item.replace('(ex Ruta 197)', '') for item in datos1]   # Hack feo...
        datos1 = filter(None, [' '.join(item.split()) for item in datos1])
        datos2 = filter(None, [' '.join(item.split()) for item in datos2])
        datos2 = ' '.join(datos2).replace('Rubros:', '')

        # formateo de datos.
        sucursal['nombre'] = datos1[0]
        sucursal['direccion'] = datos2
        sucursal['horarios'] = datos1[1] + ' ' + datos1[2]
        sucursal['telefono'] = datos1[4]
        sucursal['ciudad'] = ciudad
        
        return sucursal


class MarianoMax:

    base_url = 'http://mmax.com.ar/index.php/sucursales/sucursal-'
    suc_url = {4546: ['1', '2', '3', '5', '7'],     #Cordoba
               3649: ['4'],                         #Jesus Maria
               4471: ['6']}                         #Cruz del eje

    def __init__(self):

        self.data = []

        # Retornar un listado de sucursales Mariano Max.
        for ciudad in self.suc_url.keys():
            for i in range(len(self.suc_url[ciudad])):
                self.data.append(self.get_page_data(ciudad, 
                    self.suc_url[ciudad][i]))

        self.json = json.dumps(self.data)
            
    def get_page_data(self, ciudad, numero):
        """ Realiza el scraping de datos de la cadena Mariano Max.
        As usual una url a la vez.
        'numero' debe ser string."""
        
        htmlraw = urllib.urlopen(self.base_url + numero)
        doc = lxml.html.document_fromstring(htmlraw.read())

        sucursal = {}

        # Scraping usando xpath
        datos1 = doc.xpath('/html/body/div[2]/div/div/div/div/' +
            'div/div/div/div[2]/div[2]/div/div/h3/span/span/text()')
        datos2 = doc.xpath('//*[@class="article"]//p/text() |' +
                '//*[@class="article"]//span/text()')

        # CleanUP de datos
        datos1 = [' '.join(item.split()) for item in datos1]
        datos2 = [' '.join(item.split()) for item in datos2]

        # formateo de datos. Cada sucursal es un dict.
        sucursal['nombre'] = datos1[0]
        sucursal['direccion'] = datos2[0]
        sucursal['horarios'] = datos2[1] + datos2[2]
        sucursal['ciudad'] = ciudad

        return sucursal


if __name__ == '__main__':
    libertad = HiperLibertad()
    print libertad.json

    print '\n'

    mmax = MarianoMax()
    print mmax.json

    print '\n'

    yag = Yaguar()
    print yag.json
