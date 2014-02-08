# -*- coding: utf-8 -*-

"""
Cada Cadena de supermecados entrega una lista de sucursales. A su vez, cada sucursal es un 
diccionario cuyas claves son: 'nombre' -> Nombre de la sucursal, 'telefono' -> teléfono de 
la sucursal, 'horarios', etc
"""

import httplib
import urllib
import lxml.html


class HiperLibertad:
    """ Clase para scraping de datos del Híper Libertad"""

    base_url = 'https://www.libertadsa.com.ar/misucursal_'
    city_url = {'Cordoba': 'cordoba.php',
                'Mendoza': 'mendoza.php',
                'Salta': 'salta.php',
                'Santa Fe': 'santafe.php',
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
            self.data.append(self.get_page_data(city))

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
        _ = {}
        for sucursal in sucursales:             #Este filtro es feo... mejorar?
            datos = filter(lambda s: s != '\n        ' and s!= '\n          ', sucursal)
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

    def get_page_data(self, ciudad):
        """ Realiza el scraping de datos para la cadena Yaguar.
        El scraping es de a una url por vez """

        htmlraw = urllib.urlopen(self.base_url + self.suc_url[ciudad])
        doc = lxml.html.document_fromstring(htmlraw.read())

        # Scraping usando xpath
        sucursal = {}
    
        datos1 = doc.xpath('//*[@class]/text()')
        datos2 = doc.xpath('//*[@class]/b/text()')

        # formateo de datos.
        sucursal['nombre'] = datos1[0]
        sucursal['direccion'] = datos2[0]
        sucursal['horarios'] = datos1[1] + '-' + datos1[2]
        sucursal['telefono'] = datos1[4]
        sucursal['ciudad'] = ciudad
        
        return sucursal
        

if __name__ == '__main__':
#    libertad = HiperLibertad()
#    for i in range(len(libertad.data)):
#        print(libertad.data[i])

    yag = Yaguar()
    for i in range(len(yag.data)):
        print(yag.data[i])
#        print(yag.data[i]['horarios'] + '\n\n')


