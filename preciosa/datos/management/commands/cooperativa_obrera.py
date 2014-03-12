# -*- coding: utf-8 -*-
import logging
import requests
import pyquery
import re
import sys
from itertools import ifilter
from urlparse import urlparse, parse_qs

from datetime import date
from django.core.management.base import BaseCommand
import unicodecsv

logger = logging.getLogger(__name__)
parse_number = lambda s: float(s.replace(',', '.'))

NEXT_PAGE_RE = r'javascript:verHoja\((\d+)\)'

class ScraperCooperativaObrera(object):

    def scrape(self):
        self.browser = requests.Session()
        user_agent = {'User-agent': 'Mozilla/5.0'}

        # entrar como invitado
        self.browser.get("https://www.cooperativaobrera.com.ar//servlet/Internet.ecoop.ServletEcoopLogin?invitado=S")

        self.niveles, self.digitos, self.categorias = self._get_category_tree()

        # scrapeamos categorias que no contienen subcategorias (leaf)
        for c in ifilter(lambda c: c[1] == u'S', self.categorias):
            cat_levels = self.category_hierarchy(c[0][0])
            for p in self._scrape_product_list(c[0][0]):
                yield p + tuple(cat_levels)


    def category_hierarchy(self, categoria):
        acc = []
        cat_codes = re.findall('\d\d', categoria)
        for i in range(len(cat_codes)):
            code = ''.join(cat_codes[:i+1]) + ('00' * (self.digitos/2 - (i+1)))
            acc.append(
                next(ifilter(lambda x: x[0][0] == code, self.categorias),
                     None)[0][1]
            )
            if code == categoria:
                return acc

    def _scrape_product_list(self, categoria):
        logger.info("Scrapeando categoria: %s" % categoria)

        def inner(url, params, acc=[]):
            resp = self.browser.get(url, params=params).text
            tree = pyquery.PyQuery(resp)
            trs = tree.find('table.tabla tr:nth-child(n+3)')
            for tr in trs:
                tds = tr.findall('td')
                acc.append(
                    (
                        parse_qs(urlparse(tds[2].find('a').attrib['href']).query)['codArticulo'][0],
                        tds[2].text_content().strip(),
                        parse_number(tds[3].text_content().strip())
                    )
                )

            # hay siguiente hoja?
            f = tree.find('img[src="/ecoop/imagenes/foward.gif"]')
            if len(f) > 0:
                next_page = re.match(NEXT_PAGE_RE,
                                     f[0].getparent().attrib['href']).group(1)

                params['hoja'] = int(next_page)
                return inner(url, params, acc)
            else:
                return acc

        return inner("https://www.cooperativaobrera.com.ar/servlet/Internet.ecoop.ServletEcoop",
                     {'departamento': categoria })


    def _get_category_tree(self, url='https://www.cooperativaobrera.com.ar/ecoop/logo.jsp'):
        logger.info('Obteniendo arbol de categorías')

        js = pyquery.PyQuery(self.browser.get(url).text).find("script")[0].text

        niveles = int(re.search(r'NIVELES=(\d+)', js, re.UNICODE).group(1))
        digitos = int(re.search(r'DIGITOS=(\d+)', js, re.UNICODE).group(1))
        categorias = re.findall("((\d{%d})([\w\s\./]+),?)+" % digitos, js, re.UNICODE)
        categoria_is_leaf = re.findall("\"(Ncover|Scover|S|N)\",?", js, re.UNICODE)

        return (niveles, digitos, zip([c[1:] for c in categorias], categoria_is_leaf))



class Command(BaseCommand):
    help = 'Scraper de Cooperativa Obrera'
    browser = None

    def handle(self, *args, **options):
        writer = unicodecsv.writer(sys.stdout)
        for p in ScraperCooperativaObrera().scrape():
            writer.writerow(p)
