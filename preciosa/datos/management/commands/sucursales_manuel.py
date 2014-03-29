# -*- coding: utf-8 -*-
u"""
convierte el json aportado por Manuel Aristarán
"""

from tools.sucursales import inferir_cadena
from tools.gis import donde_queda
from sucursales_osm import Command as CommandOSM


class Command(CommandOSM):
    args = '<file_json>'
    help = __doc__
    FILENAME = 'sucursales_manuel_%s.csv'

    def entrada(self):
        return (c['Comercio'] for c in self.data['comercios_sin_ofertas'])

    def parse_sucursal(self, comercio):

        sucursal = {}
        sucursal['lon'] = comercio['longitud']
        sucursal['lat'] = comercio['latitud']

        inferido = donde_queda(sucursal['lat'], sucursal['lon'])

        sucursal['ciudad'] = comercio['ciudad_o_barrio']
        # sucursal['ciudad_inferida'] = inferido['ciudad'].name
        sucursal['ciudad_relacionada_id'] = inferido['ciudad'].id

        sucursal['direccion'] = "%s %s" % (comercio['calle'], comercio['numero'])
        # sucursal['direccion_inferida'] = inferido['direccion']

        cadena = inferir_cadena(comercio['nombre_fantasia'])
        if cadena:
            sucursal['cadena_nombre'] = cadena[0]
            sucursal['cadena_id'] = cadena[1]
        sucursal['nombre'] = "%s %s" % (comercio['nombre_fantasia'],
                                        comercio['codigo_sucursal'])
        sucursal['provincia'] = comercio['xprovincia']
        sucursal['telefono'] = comercio['telefono']

        return sucursal
