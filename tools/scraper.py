# -*- coding: utf-8 -*-

"""
Cada Cadena de supermecados entrega un diccionario. Las llaves (keys) del diccionario son las ciudades.
Cada ciudad apunta a una lista de sucursales. A su vez, cada sucursal es un diccionario cuyas claves son:
    'Nombre' -> Nombre de la sucursal, 'TE' -> teléfono de la sucursal, 'Horarios', etc
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

        self.data = {}

        for city in self.city_url.keys():
            self.data[city] = self.get_page_data(self.city_url[city])

    def get_page_data(self, comp_url):

        htmlraw = urllib.urlopen(self.base_url + comp_url)
        doc = lxml.html.document_fromstring(htmlraw.read())
        
        #scraping de datos.
        sucursales = []
        i = 3
        while True:
            sucursales.append( doc.xpath('/html/body/div/div[9]/div[2]/div[2]/p['
                    + str(i) + ']/span/text() | /html/body/div/div[9]/div[2]/div[2]/p['
                    + str(i) + ']/span[2]/span/text()' ) )
            if not sucursales[-1]:
                del sucursales[-1]
                break
            i += 1

        # Formato de datos: Lista de sucursales. Cada sucursal es un 
        # dict (claves: 'Nombre', 'Direccion', etc
        format_datos = []
        _ = {}
        for sucursal in sucursales:
            datos = filter(lambda s: s != '\n        ' and s!= '\n          ', sucursal)
            _['Nombre'] = datos[0]
            _['Direccion'] = datos[1]
            _['CP'] = datos[2]
            _['TE'] = datos[3]
            _['Horarios'] = datos[4]
            _['Director'] = datos[5]
            format_datos.append(_)
        return format_datos


if __name__ == '__main__':
    libertad = HiperLibertad()
    print(libertad.data['San Juan'])
    print('\n\n')
    print(libertad.data['Cordoba'])
