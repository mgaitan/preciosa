"""
script para el ticket #199

Se unifican productos repetidos a "upc" de 13 digitos.
"""

from preciosa.precios.models import Producto


def main():
    prods13 = Producto.objects.extra(where=["CHAR_LENGTH(upc) = 13"])
    prods12 = Producto.objects.extra(where=["CHAR_LENGTH(upc) = 12"])

    for p13 in prods13:
        try:
            p12 = prods12.get(upc=p13.upc[:12])
        except Producto.DoesNotExist:
            continue

        p13.agregrar_descripcion(descripcion=p12.descripcion)
        for precio in p12.precios.all():
            precio.producto = p13
            precio.save(update_fields='producto')
        p12.delete()


if __name__ == '__main__':
    main()
