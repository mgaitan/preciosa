import urllib2
from django.core.files.images import ImageFile
from django.core.files.temp import NamedTemporaryFile
from preciosa.precios.models import Producto

from utils import get_logger


logger = get_logger('walmart.log')


def get_thumb(producto):
    try:
        url = "https://www.walmartonline.com.ar/images/products/img_large/%sL.jpg" % producto.upc

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib2.urlopen(url).read())
        img_temp.flush()

        producto.foto.save(producto.upc + '.jpg', ImageFile(img_temp))
        print('Ok %s' % producto.upc)
    except Exception, e:
        logger.error('Failed %s: ' % producto.upc + str(e))


if __name__ == '__main__':
    productos = Producto.objects.filter(upc__isnull=False,
                                        foto='',
                                        precio__sucursal__cadena__nombre="Walmart")

    for producto in productos:
        get_thumb(producto)
