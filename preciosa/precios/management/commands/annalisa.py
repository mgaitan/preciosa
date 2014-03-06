# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from optparse import make_option
from annoying.functions import get_object_or_None
from django.db.models import Q

import requests
from preciosa.precios.models import Producto, Marca, Categoria


class Annalisa(object):

    API_ANALYZE = 'http://preciosaannalisa.heroku.com/api/analyze?q='

    MAPA_CLAVES = {'volumen': 'contenido',
                   'peso': 'contenido',
                   'unidad_peso': 'unidad_medida',
                   'unidad_volumen': 'unidad_medida',
                   }
    MAPA_UNIDADES = {'gramo': Producto.UM_GRAMO,
                     'kilogramo': Producto.UM_KILO,
                     'litro': Producto.UM_L,
                     'centimetro cubico': Producto.UM_ML,
                     'mililitro': Producto.UM_ML,
                     }

    def analyze(self, q):
        """consulta al webservice. dado una descripcion, devuelve toda la data inferida
           que puede"""
        result = requests.get(Annalisa.API_ANALYZE + q)
        return self.normalizar(result.json())

    def normalizar(self, data):
        """normaliza claves y unidades devueltas por Annalisa a lo que necesita el
           modelo Producto"""
        result = {}
        for k1, k2 in Annalisa.MAPA_CLAVES.iteritems():
            if k1 in data:
                result[k2] = data[k1]

        if 'unidad_medida' in result:
            result['unidad_medida'] = Annalisa.MAPA_UNIDADES.get(
                result['unidad_medida'], None)

        if 'marcaid' in data:
            result['marca'] = get_object_or_None(Marca, id=data['marcaid'])

        if 'categoriaid' in data:
            result['categoria'] = get_object_or_None(
                Categoria, id=data['categoriaid'])

        return result


class Command(BaseCommand):
    help = 'Utiliza Annalisa para inferir detalles a partir de la descripcion'
    option_list = BaseCommand.option_list + (
        make_option('--force-marca',
                    action='store_true',
                    dest='force_marca',
                    default=False,
                    help='Fuerza la marca encontrada por Annalisa, '
                    'aunque esté definida en la instancia'),
        make_option('--force-categoria',
                    action='store_true',
                    dest='force_categoria',
                    default=False,
                    help='Fuerza la categoria encontrada por Annalisa, '
                    'aunque esté definida en la instancia'),
        make_option('--force-unidad',
                    action='store_true',
                    dest='force_unidad',
                    default=False,
                    help='Fuerza la unidad encontrada por Annalisa, '
                    'aunque esté definida en la instancia'),
        make_option('--force-cantidad',
                    action='store_true',
                    dest='force_cantidad',
                    default=False,
                    help='Fuerza la cantidad encontrada por Annalisa, '
                    'aunque esté definida en la instancia'),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.anna = Annalisa()

    def handle(self, *args, **options):

        def update(producto, data):
            for k in data:
                actual = getattr(producto, k)
                # cambia por lo que encontro si Force o si no existe actual
                force = options.get('force_' + k, False)
                nuevo = data[k] if force else actual or data[k]
                setattr(producto, k, nuevo)
                if k == 'unidad':
                    import ipdb; ipdb.set_trace()
            producto.save(update_fields=data.keys())
            return producto

        for producto in Producto.objects.filter(Q(marca__isnull=True) |
                                                Q(contenido__isnull=True) |
                                                Q(categoria__oculta=False))[30:]:
            self.stdout.write(u'%s' % producto)
            old = producto.__dict__
            old['categoria'] = producto.categoria
            old['marca'] = producto.marca
            data = self.anna.analyze(producto.descripcion)
            update(producto, data)
            for k in data:
                self.stdout.write(u'  %s: ' % k)
                self.stdout.write(u'      original: %s' % old[k])
                self.stdout.write(u'      annalisa: %s' % data[k])
                self.stdout.write(u'      nuevo: %s' % getattr(producto, k))

        self.stdout.write(u'Fin!')
