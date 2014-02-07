import json
from glob import glob
from pyquery import PyQuery

from preciosa.precios.models import Categoria, Producto, Sucursal, Precio

WALMART_ONLINE = Sucursal.objects.get(nombre='Walmart Online')
URL = "https://www.walmartonline.com.ar/Detalle-de-articulo.aspx?upc="


def parse(upc):
    """dado un UPC, devuelve un diccionario de datos scrappeados
    de la pagina de detalle del producto"""

    def cat(pq):
        html_categ = [s.strip().lower() for s in pq('div.tituloNaranja').text().strip().split(u'\xa0>')
                      if s.strip()]
        match = Categoria.objects.filter(nombre__icontains=html_categ[-1])
        if len(match) == 1:
            return match[0]
        else:
            for m in match:
                ancestors = [c.nombre.lower() for c in m.get_ancestors()]
                if ancestors == html_categ[:2]:
                    return m

    pq = PyQuery(URL + str(upc))
    categoria = cat(pq)

    descripcion = pq('span#lblTitle').text()
    precio = clean_precio(pq('span#lblPrice').text())
    um = pq('span#lblUnit').text()
    um = Producto.UM_TRANS.get(um, um)
    notas = 'PrecioGranel: %s' % pq('span#lblPricexUnit').text()

    return {'categoria': categoria, 'descripcion': descripcion,
            'precio': precio, 'unidad_medida': um,
            'notas': notas, 'upc': upc}



def clean_precio(precio):
    return precio.replace('$','').replace(',', '')


def entry(**kw):
    """commit producto y/o precio"""
    precio = kw.pop('precio')
    producto, _ = Producto.objects.get_or_create(**kw)

    precio = Precio.objects.create(producto=producto,
                                   sucursal=WALMART_ONLINE,
                                   precio=precio)
    print precio





def load_jsons():

    fallan = []

    for fixture in glob('/home/tin/lab/preciosa/fixtures/w2/*json'):
        data = json.load(open(fixture))
        for prod in data:
            if Producto.objects.filter(upc=prod['upc']).exists():
                continue

            um = Producto.UM_TRANS.get(prod['WMNumber'], prod['WMNumber'])
            try:
                producto = Producto.objects.create(descripcion=prod['Description'],
                                                   upc=prod['upc'],
                                                   unidad_medida=um,
                                                   categoria=parse(prod['upc']),
                                                   notas='PrecioGranel: %s' % prod["PrecioGranel"],
                                                )

                precio = Precio.objects.create(producto=producto,
                                               sucursal=WALMART_ONLINE,
                                               precio=clean_precio(prod['Precio']))

                print precio
            except:
                fallan.append(prod['upc'])
                print 'falla --->', prod['upc']


if __name__ == '__main__':
    load_jsons()