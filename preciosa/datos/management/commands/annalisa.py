# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from annoying.functions import get_object_or_None
from django.db.models import Q
import logging
import requests
from preciosa.precios.models import Producto, Marca, Categoria

logger = logging.getLogger('main')


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
            if result['categoria'] and result['categoria'].depth != 3:
                del result['categoria']

        return result


class Command(BaseCommand):
    help = 'Utiliza Annalisa para inferir detalles a partir de la descripcion'
    
    def add_arguments(self, parser):

        parser.add_argument('--force-marca',
                    action='store_true',
                    dest='force_marca',
                    default=False,
                    help='Fuerza la marca encontrada por Annalisa, '
                    'aunque esté definida en la instancia'),
        parser.add_argument('--force-categoria',
                    action='store_true',
                    dest='force_categoria',
                    default=False,
                    help='Fuerza la categoria encontrada por Annalisa, '
                    'aunque esté definida en la instancia'),
        parser.add_argument('--force-unidad',
                    action='store_true',
                    dest='force_unidad_medida',
                    default=False,
                    help='Fuerza la unidad encontrada por Annalisa, '
                    'aunque esté definida en la instancia'),
        parser.add_argument('--force-cantidad',
                    action='store_true',
                    dest='force_cantidad',
                    default=False,
                    help='Fuerza la cantidad encontrada por Annalisa, '
                    'aunque esté definida en la instancia'),

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.anna = Annalisa()

    def handle(self, *args, **options):

        if int(options['verbosity']) == 0:
            logger.removeHandler('console')

        def update(producto, data):
            for k in data:
                actual = getattr(producto, k)
                # cambia por lo que encontro si Force o si no existe actual
                force = options.get('force_' + k, False)
                nuevo = data[k] if force else actual or data[k]
                setattr(producto, k, nuevo)
            producto.save(update_fields=data.keys())
            return producto

        for producto in Producto.objects.filter(Q(marca__isnull=True) |
                                                Q(contenido__isnull=True) |
                                                Q(categoria__oculta=False)):
            logger.debug(u'%s' % producto)
            old = producto.__dict__
            old['categoria'] = producto.categoria
            old['marca'] = producto.marca
            data = self.anna.analyze(producto.descripcion)
            update(producto, data)
            if options['verbosity'] > 1:
                for k in data:
                    logger.debug(u'  %s: ' % k)
                    logger.debug(u'      original: %s' % old[k])
                    logger.debug(u'      annalisa: %s' % data[k])
                    logger.debug(u'      nuevo: %s' % getattr(producto, k))

        logger.debug(u'Fin!')
