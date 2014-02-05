import re
import sys
import glob
import json
import string


N_PRODUCTOS = 500   # cantidad de productos con acuerdo
HEADERS = ('id', 'descripcion', 'marca', 'contenido', 'unidad_medida', 'categoria',
           'precio_norte', 'precio_sur')
normalize_number = lambda x: x.strip().replace(',', '.').replace('$ ', '')
FILTERS = (normalize_number, string.capitalize, string.capitalize, normalize_number,
           string.lower, string.capitalize, normalize_number, normalize_number)

assert len(HEADERS) == len(FILTERS)


def parser(path):
    productos = []
    cadena = None
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        cells = re.split(" {2,}", line)
        if len(cells) == 1 and cadena is None:
            cadena = cells[0]
        elif len(cells) == len(HEADERS):
            filtered_cells = [f(cell) if callable(f) else cell
                              for f, cell in zip(FILTERS, cells)]
            product = dict(zip(HEADERS, filtered_cells))
            productos.append(product)

    ids = [d['id'] for d in productos]
    conflictivos = set([x for x in ids if ids.count(x) > 1])
    return {'cadena': cadena, 'productos': productos,
            'ids_conflictivos': list(conflictivos)}


def main():
    if len(sys.argv) != 2:
        print "Usage: %s path" % __file__
        sys.exit(0)

    files = glob.glob(sys.argv[1])
    result = []
    for path in files:
        result.append(parser(path))

    json.dump(result, open('precios.json', 'w'), indent=2)
    return result

if __name__ == '__main__':
    result = main()