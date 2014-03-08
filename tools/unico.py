# -*- coding: utf-8 -*-
import logging
import requests
import json
import sys
import re

from pyquery import PyQuery as pq
from bs4 import BeautifulSoup

from datetime import date
from utils import UnicodeCsvWriter

h1 = logging.StreamHandler(stream=sys.stdout)
h1.setLevel(logging.DEBUG)

logger = logging.getLogger('unico')
logger.addHandler(h1)
logger.setLevel(logging.DEBUG)

# all urls needed
URL = {
    'base': 'http://www.unicosupermercados.com.ar',
    'compra-online': '/ofertas',
}


# utility to get the whole url
def get_url(name):
    return URL['base'] + URL.get(name, name)

# browser creation
browser = requests.Session()

# set a proper user agent
user_agent = {'User-agent': 'Mozilla/5.0'}

# needed to set some cookies from the server into our session
r = browser.get(get_url('compra-online'), headers=user_agent)

query = pq(r.content)

# get all the urls for products
urls = [u.values()[0] for u in query('ul > li > ul > li > a') \
        if not u.values()[0].startswith('ofertas')]

logger.info('Found %s categories.', len(urls))

fp = open('unico.csv', 'wb')
csvwriter = UnicodeCsvWriter(fp)
csvwriter.writerow(['desc', 'precio', 'plu', 'precio x unidad',
                    'link', 'imagen', 'rubro', 'fecha'])


def scrap_url(url, scrap_pages=False):
    logger.debug('Downloading: %s', url)
    r = browser.get(get_url('/' + url), headers=user_agent)
    query = pq(r.content)
    # get all products for this category
    trs = query('table.tabla_productos > tbody > tr')

    if scrap_pages:
        paginator = query('div.paginador > a')
        pages = (len(paginator) / 2) - 2  # the links appear twice each one

        logger.debug('Found %s page(s) in "%s"', pages, url)

        if pages > 1:
            for a in paginator[2:- (-1 - pages)]:
                url = a.values()[0]\
                       .replace('http://www.unicosupermercados.com.ar/', '')
                scrap_url(url)

    for i in range(len(trs)):
        id = trs.eq(i).attr('id')[1:]  # remove the first 'p'
        image = trs.eq(i).find('td.img > a').attr('href')
        if image is not None:
            image = get_url('/' + image)
        else:
            image = ''
        description = trs.eq(i).find('td.descripcion > p').text()
        price = trs.eq(i).find('td.precio > span > strong').text()

        category = ' > '.join(query('div.titulo > p.titulo_categoria')\
                              .text().split(' | ')[1:])

        link = unit_price = ''

        row = [description, price, id, unit_price, link,
               image, category,  date.today().isoformat()]

        csvwriter.writerow(row)


for url in urls:
    scrap_url(url, scrap_pages=True)


fp.close()
