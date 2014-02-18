# -*- coding: utf-8 -*-
u"""Importador de marcas desde archivos CSV
El formato es el siguiente:

    fabricante,url_logo_fabricante
    marca1,url_logo_marca1
    marca2,url_logo_marca2

o bien

    fabricante
    marca1
    marca2

La primer linea es el nombre del fabricante y su logo, y luego son marcas
asociadas a ese fabricante. Una url de logo puede estár vacía.
"""
import os
import glob
import logging
import urllib2

# Get an instance of a specific named logger

from django.core.files.images import ImageFile
from django.core.files.temp import NamedTemporaryFile

from preciosa.precios.models import EmpresaFabricante, Marca
from tools.utils import UnicodeCsvReader
from django.core.management.base import BaseCommand


logger = logging.getLogger('imports')


class Command(BaseCommand):
    args = u'csv1 csv2 ...'
    help = __doc__

    def handle(self, *args, **options):

        for path in args:
            for csv_file in glob.glob(path):
                data = UnicodeCsvReader(open(csv_file, 'r'))
                fila = data.next()
                if len(fila) == 1:
                    fila = (fila[0], None)
                empresa, url_logo_empresa = fila
                empresa, _ = EmpresaFabricante.objects.get_or_create(nombre=empresa)
                if _:
                    logger.debug(u'Empresa nueva: %s' % empresa)
                else:
                    logger.debug(u'Empresa existente: %s' % empresa)
                if url_logo_empresa:
                    self.set_thumb(empresa, url_logo_empresa)

                for fila in data:
                    if len(fila) == 1:
                        fila = (fila[0], None)
                    marca, url_logo = fila
                    marca, creada = Marca.objects.get_or_create(nombre=marca)
                    if creada:
                        logger.debug(u'Marca nueva: %s' % marca)
                    elif marca.fabricante and marca.fabricante != empresa:
                        logger.error(u'Marca asociada a otra empresa: %s' % marca)
                    elif not marca.fabricante:
                        logger.debug(u'Marca existente sin asociar: %s' % marca)
                        marca.fabricante = empresa
                        marca.save()
                    else:
                        logger.debug(u'Marca existente: %s' % marca)
                    if url_logo:
                        self.set_thumb(marca, url_logo)

    def set_thumb(self, marca_o_fabricante, url):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        if marca_o_fabricante.logo:
            logger.debug(u'    Logo ya existe para %s' % marca_o_fabricante)
            return

        try:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(opener.open(url).read())
            img_temp.flush()
            marca_o_fabricante.logo.save(os.path.basename(url), ImageFile(img_temp))
            logger.debug(u'    Conseguimos el logo de %s' % marca_o_fabricante)
        except Exception, e:
            logger.error(u'    Error "%s" %s: %s' % (e, marca_o_fabricante, url))
