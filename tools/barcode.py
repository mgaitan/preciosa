"""
utilidades para chequear codigos de barra
"""

def checksum(code):
    """calcula el checksum para codigos
    de barra segun algoritmo UPC/GTIN

    NO GARANTIZA QUE UN CODIGO SEA VALIDO
    / *no chequea longitud*
    """

    total = 0

    for (i, c) in enumerate(code):
        if i % 2 == 1:
            total = total + int(c)
        else:
            total = total + (3 * int(c))

    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)


def es_valido(code):
    return checksum(code[:-1]) == code[-1]


def normalizar(code):
    """work in progress. """
    largo = len(code)
    if largo < 7:
        # mayormente frutas y verduras. No es identificador
        return None
    if code.startswith('4000'):
        # dummy code?  chequear.
        # codigo interno del vendedor
        return None
    elif largo in (7, 12):
        return code + checksum(code)
    elif largo in (8, 13) and es_valido(code):
        return code



