"""
Este modulo es un importado de marcas desde archivos CSV

[fabricante,url_logo_fabricante]
marca, url_logo

El csv la primer linea es el nombre del fabricante y su logo,
y despues son marcas asociadas a ese fabricante

"""
import os
import csv
import urllib2
from django.core.files.images import ImageFile
from django.core.files.temp import NamedTemporaryFile
from utils import get_logger


logger = get_logger('import_marcas.log')



def get_thumb(marca, url):
    try:

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib2.urlopen(url).read())
        img_temp.flush()
        marca.logo.save(os.path.basename(url), ImageFile(img_temp))
        logger.info('Conseguimos el logo de %s' % marca
    except Exception, e:
        logger.error('Failed %s: ' % producto.upc + str(e))

