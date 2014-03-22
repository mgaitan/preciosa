# -*- coding: utf-8 -*-
"""convierte el csv de productos original
a uno normalizado para importar
"""

import sys
import unicodecsv as csv
from preciosa.datos.adaptors import PRODUCTO_COLS
from preciosa.precios.models import Producto
from preciosa.datos.management.commands.annalisa import Annalisa

try:
    from progress.bar import Bar
except ImportError:
    print """Instalaste las dependecias extra?:
        $ pip install -r requirements/extra.txt  """
    raise


EJEMPLO = """400832115868;LÁMPARA DE BAJO CONSUMO OSRAM 20WTS.;1;Un;6;Hab
400832119162;LÁMPARA OSRAM 20WTS.DECOSTAR HALO;1;Un;20;Hab
400832119164;LÁMPARA OSRAM 50WTS.DECOSTAR HALO;1;Un;20;Hab
400832121215;LÁMPARA OSRAM 28W.HALOGENA CLASSI;1;Un;20;Hab"""

headers = ('upc', 'descripcion', 'contenido',
           'unidad_medida', 'unidades_por_lote', 'oculto')

MAPA_UNIDADES = {'Gr': Producto.UM_GRAMO,
                 'Un': Producto.UM_UN,
                 'Bl': Producto.UM_UN,
                 'Lt': Producto.UM_L,
                 'Cc': Producto.UM_ML,
                 'Ml': Producto.UM_ML,
                 'Kg': Producto.UM_KILO,
                 'Mt': Producto.UM_M,
                 'M2': Producto.UM_M2,
                 'Cm': Producto.UM_ML
                 }

anna = Annalisa()


def main():
    dialect = csv.Sniffer().sniff(EJEMPLO)
    reader = csv.reader(open(sys.argv[1]), dialect=dialect)
    writer = csv.DictWriter(open('productos.csv', 'w'), fieldnames=PRODUCTO_COLS)
    writer.writeheader()
    bar = Bar('Normalizando CSV', suffix='%(percent)d%%')
    for l in bar.iter(reader):
        data = normalizar(dict(zip(headers, l)))
        writer.writerow(data)


def normalizar(data):
    data['oculto'] = data['oculto'] == 'Des'
    data['unidad_medida'] = MAPA_UNIDADES[data['unidad_medida']]
    try:
        existe = Producto.objects.get(upc=data['upc'])
        data['id'] = existe.id

    except Producto.DoesNotExist:
        return data
        """
        analisis = anna.analyze(data['descripcion'])
        if 'marca' in analisis:
            data['marca_id'] = analisis['marca'].id

        if 'categoria' in analisis:
            data['categoria_id'] = analisis['categoria'].id
        """
    return data


if __name__ == '__main__':
    main()
