# -*- coding: utf-8 -*-
import unicodedata


def normalizar(cadena):
    """devuelve una version normalizada

        >>> normalizar(u'Ñonos útiles')
        'nonos utiles'
    """
    try:
        normal = unicodedata.normalize('NFKD', cadena)
    except TypeError:
        cadena = cadena.decode('iso-8859-1')
        normal = unicodedata.normalize('NFKD', cadena)
    return normal.encode('ASCII', 'ignore').lower()
