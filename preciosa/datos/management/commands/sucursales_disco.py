# -*- coding: utf-8 -*-
u"""
convierte el dataset de sucursales disco. ref #61
"""
import re
from tools.sucursales import inferir_ciudad
from sucursales_osm import Command as CommandOSM

BARRIOS_CBA = ["General Paz", "24 De Setiembre", "Cerro", "Centro",
               "Alta Alberdi", u"Alta San Mart\u00edn", u"Alta C\u00f3rdoba",
               u"Nueva C\u00f3rdoba", "P. De Los Andes", "P. V. Sarfield",
               "R. Martinolli", u"Jard\u00edn", "J. B. Alberdi"]


class Command(CommandOSM):
    args = '<file_json>'
    help = __doc__
    FILENAME = 'sucursales_disco_%s.csv'

    def entrada(self):
        sucursales = []
        for prov in self.data['sucursales']['provincia']:
            provincia = prov["nombre_provincia"]["#text"]
            region_k = prov["region"]
            if not isinstance(region_k, list):
                region_k = [region_k]
            for region in region_k:
                barrio_k = region["barrio"]
                if not isinstance(barrio_k, list):
                    barrio_k = [barrio_k]
                for barr in barrio_k:
                    barrio = barr["nombre_barrio"]["#text"]

                    sucursal_k = barr['sucursal']
                    if not isinstance(sucursal_k, list):
                        sucursal_k = [sucursal_k]
                    for suc in sucursal_k:
                        s = {'provincia': provincia, 'barrio': barrio}
                        s['nombre'] = suc['sucursal_nombre']['#text']
                        s['direccion'] = suc['sucursal_dir']['#text']
                        sucursales.append(s)
        return sucursales

    def parse_sucursal(self, suc):

        s = {}
        s['nombre'] = suc['nombre']
        s['cadena'] = 'Disco'
        s['cadena_id'] = 6

        dire = re.findall(r'(^.*)\.([ \d / -]+)$', suc['direccion'])
        if dire:
            s['direccion'] = dire[0][0].strip()
            s['telefono'] = dire[0][1].strip()
        else:
            s['direccion'] = suc['direccion']

        if suc['barrio'] in BARRIOS_CBA:
            # simplifico a cba
            suc['barrio'] = u'Córdoba'

        ciudad_inferida = inferir_ciudad(suc['barrio'], suc['provincia'])

        if ciudad_inferida:

            s['ciudad'] = suc['barrio']
            s['ciudad_inferida'] = ciudad_inferida[0]
            s['ciudad_relacionada_id'] = ciudad_inferida[2]

        s['provincia'] = suc['provincia']
        return s
