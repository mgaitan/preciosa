# -*- coding: utf-8 -*-
import logging
import requests
import json
import sys
import re

from bs4 import BeautifulSoup

from datetime import date
from utils import UnicodeCsvWriter

h1 = logging.StreamHandler(stream=sys.stdout)
h1.setLevel(logging.DEBUG)

logger = logging.getLogger('jumbo')
logger.addHandler(h1)
logger.setLevel(logging.DEBUG)

# all urls needed
URL = {
    'base': 'https://www.jumboacasa.com.ar',
    'prehome': '/Login/PreHome.aspx',
    'login': '/Login/Invitado.aspx',
    'articulos': '/Comprar/HomeService.aspx/ObtenerArticulosPorMenuMarcaFamilia',
    'menu': '/Comprar/Menu.aspx?SId=ie4i2u52024',
    'image': '/JumboComprasArchivos/Archivos/{0}.jpg'
}


# utility to get the whole url
def url(name):
    return URL['base'] + URL[name]

# browser creation
browser = requests.Session()

# set a proper user agent
user_agent = {'User-agent': 'Mozilla/5.0'}

# needed to set some cookies from the server into our session
r = browser.get(URL['base'], headers=user_agent)
r = browser.get(url('prehome'), headers=user_agent)
r = browser.get(url('login'), headers=user_agent)
r = browser.get(url('menu'), headers=user_agent)

# get categories from the last level
regex = re.compile('.*Array\((?P<id>\d{1,5}),\'(?P<categoria>.*)\',null.*')

menu = regex.findall(r.content)

logger.info('Found %s categories.', len(menu))

headers = {
    'User-agent': 'Mozilla/5.0',
    'Content-type': 'application/json',
    'Accept': 'application/json, text/plain',
}

fp = open('jumbo.csv', 'wb')
csvwriter = UnicodeCsvWriter(fp)
csvwriter.writerow(['desc', 'precio', 'plu', 'precio x unidad',
                    'link', 'imagen', 'rubro', 'fecha'])

for id, name in menu:
    code = 'ids={0}&' \
           'cat1=&' \
           'cat2=&' \
           'lastCat=&' \
           'marca=&' \
           'producto=&' \
           'pager=&' \
           'page=menu&' \
           'ordenamiento=0'

    logger.info('Downloading category: "%s"', name)
    r = browser.post(url('articulos'),
                 headers=headers,
                 data=json.dumps({'code': code.format(id)}))

    soup = BeautifulSoup(json.loads(r.content)['d'])
    items = soup.findAll('items')

    category = soup.findAll('title')[-1].text


    # sometimes I get many items and some of them are empty
    # I choose only the first one that is not empty
    item_exist = False
    for item in items:
        if item.text:
            item_exist = True
            break

    if not item_exist:
        logger.warning('Category "%s" (id: %s) was excluded '
                       'because we don\'t receive any items.', name, id)
        continue

    products = item.text.split(u'\u25ca0\u25ca')

    logger.info('Found %s products in "%s"', len(products), name)

    for p in products:
        # HACK: remove no-needed characters
        p = p.replace(u'\xac', '')
        p = p.replace(u',o', '')

        if not p:
            logger.info('Excluding product "%s". It seems to be empty.', p)
            continue

        try:
            ids, info = p.split(u'\u25ca\u25ca')[:2]
        except ValueError:
            logger.error('There was some error with '
                         'product "%s". Excluding this product.', p)
            # import ipdb;ipdb.set_trace()
            continue

        description, price_unit, price_x, = info.split(u'\u25ca')[:3]

        # FIXME: this number is the 'id' that Jumbo uses to add the
        # article to the cart, but it's not the EN-13 code
        try:
            id, n, image_id = ids.split(',')
        except ValueError:
            # some products have an extra comma :)
            n_1, id, n_2, image_id = ids.split(',')

        link = ''

        if image_id == '0':
            image = ''
        else:
            image = url('image').format(image_id)

        row = [description, price_x, id, price_unit,
               link, image, category, date.today().isoformat()]

        urow = []
        for r in row:
            if isinstance(r, unicode):
                urow.append(r)
            else:
                urow.append(r.decode('utf-8'))

        try:
            csvwriter.writerow(urow)
        except UnicodeDecodeError:
            logger.error('Some of the columns in this '
                         'row are not Unicode compatible.')

fp.close()
