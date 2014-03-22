# -*- coding: utf-8 -*-
"""
basado en el csv de datos. infiere marcas
"""

from tools.texto import normalizar
import re
from preciosa.precios.models import Categoria


r = open('../articulos/art.csv')
descrip = [l.split(';')[1] for l in r]
descrip = [re.search(r'([^\d]*)', s).group().strip() for s in descrip]
descrip = set(descrip)

cat = [c.nombre for c in Categoria.objects.all()]
cat = set(cat)
cat = [c.replace('/', ' ').replace('-', ' ') for c in cat]
cat = set([c.replace('  ', ' ').lower() for c in cat])

posibles_marcas = []
for desc in descrip:
    desc_normal = normalizar(desc)
    for c in cat:
        if ' ' + c + ' ' in desc_normal:
            posibles_marcas.append(normalizar(desc_normal).replace(' ' + c + ' ', '').strip())
        elif desc_normal.startswith(c + ' '):
            posibles_marcas.append(normalizar(desc_normal).replace(c + ' ', '').strip())

