# -*- coding: utf-8 -*-

"""
Cada Cadena de supermecados entrega una lista de sucursales. A su vez, cada sucursal es un 
diccionario cuyas claves son: 'nombre' -> Nombre de la sucursal, 'telefono' -> teléfono de 
la sucursal, 'horarios', etc
"""

import urllib
import lxml.html
import json


class HiperLibertad:
    """ Clase para scraping de datos del Híper Libertad"""

    base_url = 'https://www.libertadsa.com.ar/misucursal_'
    city_url = {'Cordoba': 'cordoba.php',
                'Mendoza': 'mendoza.php',
                'Salta': 'salta.php',
                'Rosario': 'santafe.php',
                'Resistencia': 'chaco.php',
                'Posadas': 'misiones.php',
                'San Juan': 'sanjuan.php',
                'San Miguel': 'tucuman.php',
                'Santiago del Estero': 'santiago.php'}

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
    suc_url = {'CABA': 'iframe_Autopista.asp',
               'Santa Fe': 'iframe_sucursalSantaFe.asp',
               'Resistencia': 'iframe_SucursalesChaco.asp',
               'Mendoza': 'iframe_SucursalesMendoza.asp',
               'Bahia Blanca': 'iframe_Sucursalesbahiablanca.asp',
               'Campana': 'iframe_SucursalesCampana.asp',
               'Moreno': 'iframe_SucursalesMoreno.asp',
               'Jose C Paz': 'iframe_SucursalesjoseCpaz.asp',
               'Cordoba': 'iframe_sucursalescordoba.asp',
               'Tigre': 'iframe_SucursalesTigre.asp',
               'Neuquen': 'iframe_sucursalesneuquen.asp',
               'Salta': 'iframe_sucursalesSalta.asp',
               'Mar del Plata': 'iframe_MardelPlata.asp',
               'San Juan': 'iframe_SanJuan.asp'}

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
    suc_url = {'Cordoba': ['1', '2', '3', '5', '7'],
               'Jesus Maria': ['4'],
               'Cruz del eje': ['6']}

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
#    libertad = HiperLibertad()
#    print libertad.json

    mmax = MarianoMax()
    print mmax.json

