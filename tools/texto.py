# -*- coding: utf-8 -*-
import unicodedata


def normalizar(cadena):
    """devuelve una version normalizada

        >>> normalizar('Ñonos útiles')
        'nonos utiles'
    """
    return unicodedata.normalize('NFKD', cadena).encode('ASCII',
                                                        'ignore').lower()