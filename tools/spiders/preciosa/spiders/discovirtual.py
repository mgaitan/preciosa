from scrapy.spider import Spider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from preciosa.items import DiscoVirtualProduct
from datetime import datetime
from collections import namedtuple
import re
import pytz


def get_product_data(products_list):
    """Will find all links that have JavaScript:MArt(id, 'price');
       as their href property and extract the id and price"""
    match = re.findall(r"JavaScript:MArt\((\d+)\,\'(\d*\.?\d*)\'\);", products_list)
    if match:
        return set(match)
    return None


def get_next_page(products_list):
    """Will find ">&gt;&gt;</a> which indicates the a next page link exists"""
    return re.search(r"\"\>\&gt\;\&gt\;\<\/a\>", products_list)


def stringify_postdata(postdata):
    strings_list = []
    for key, value in postdata.iteritems():
        if key in ('textoBusqueda', 'pecControlUniqueID'):
            continue
        strings_list.append('"{}":{}'.format(key, value))

    # all other values expect str:int, these are str:str
    strings_list.append('"textoBusqueda":""')
    strings_list.append('"pecControlUniqueID":""')
    return '{%s}' % ','.join(strings_list)


def get_date():
    """Returns current date in Cordoba Argentina
       in the format YYYYMMDD"""
    fmt = "%Y%m%d"
    d = datetime.now(pytz.timezone('America/Argentina/Cordoba'))
    return d.strftime(fmt)


Category = namedtuple('Category', ['id', 'name'])
ProductLink = namedtuple('ProductLink', ['id', 'price'])


def parse_categories(cat_str):
    """Parses this reponse http://pastebin.com/tS3CrKJE"""
    categories = []
    for line in cat_str.split('\n'):
        if not 'null' in line:
            continue  # we process ending nodes only
        cat = parse_line(line)
        if cat:
            categories.append(cat)
    return categories


def parse_line(line):
    """Extracts the id and category name from lines
       that have Array(id, 'name') format"""
    match = re.findall("Array\((\d+),\'(.+)\'", line)
    if match:
        return Category._make(*match)
    return None


class DiscoVirtualSpider(Spider):
    _login_url = 'https://www3.discovirtual.com.ar/Login/Invitado.aspx'
    _home_url = 'https://www3.discovirtual.com.ar/Comprar/Home.aspx'
    _products_list_url = 'https://www3.discovirtual.com.ar/ajaxpro/_MasterPages_Home,DiviComprasWeb.ashx?method=PecActualizar'
    _products_detail_url = 'https://www3.discovirtual.com.ar/Comprar/ArticuloMostrar.aspx'
    _categories_url = 'https://www3.discovirtual.com.ar/Comprar/Menu.aspx?IdLocal=9235&IdTipoCompra=4&Fecha={date}'
    _postdata = {
        'pecActualizarFuncion': '0',
        'pecControlUniqueID': '',
        'pecTablaOrden': '1',
        'pecTablaElementoOrden': '0',
        'pecOpcion': '1',
        'textoBusqueda': '',
        'idMenu': '0',
        'idPromo': '0',
        'idPECListaCompraParametro': '0',
        'idPedido': '0',
        'sortDirection': '0',
        'sortExpresion': '0',
        'paginacion': '20',
        'paginaActual': '0',
        'idMiLista': '0',
        'visualizarFotosArticulos': 'true'
    }

    name = 'discovirtual'
    allowed_domains = ['discovirtual.com.ar']
    start_urls = [_login_url]

    def parse(self, response):
        if(self.is_home_response(response)):
            return Request(url=self.prepare_categories_url())
        elif(self.is_categories_response(response)):
            return self.get_categories(response)

    def prepare_categories_url(self):
        return self._categories_url.format(date=get_date())

    def is_home_response(self, response):
        return response.url == self._home_url

    def is_categories_response(self, response):
        return response.url == self.prepare_categories_url()

    def get_categories(self, response):
        for cat in parse_categories(response.body):
            postdata = dict(self._postdata)  # copy the _formdata dict
            postdata['idMenu'] = cat.id
            yield self.build_products_listing_request(postdata, cat.name)

    def parse_products_list(self, response):
        assert 'Productos Sugeridos' in response.body  # this should always be here
        # get links of products but not the ones in 'Productos Sugeridos' pane
        products_list = response.body.split('Productos Sugeridos')[0]

        for link in get_product_data(products_list):
            product_link = ProductLink(*link)
            category_name = response.meta['category_name']
            yield self.build_product_detail_request(product_link, category_name)

        if get_next_page(products_list):
            yield self.build_products_listing_request(response.meta['postdata'],
                                                      response.meta['category_name'])

    def parse_product_detail(self, response):
        hxs = Selector(response)
        item = DiscoVirtualProduct()
        item['id'] = response.meta['product_link'].id
        item['price'] = response.meta['product_link'].price
        item['category'] = response.meta['category_name']
        item['name'] = hxs.xpath('//*[@id="pDescArticulo"]').css('td.tit-gris-1::text').extract()[0].strip()
        item['unit_price'] = hxs.xpath('//*[@id="pDescArticulo"]').css('span.txt-3 span::text').extract()[0].strip()
        item['img_url'] = hxs.xpath('//*[@id="pImgArticulo"]/img/@src').extract()[0]
        return item

    def build_products_listing_request(self, postdata, category_name):
        postdata['paginaActual'] = str(int(postdata['paginaActual']) + 1)  # inc page number
        return Request(url=self._products_list_url, method='POST',
                       meta={'postdata': postdata, 'category_name': category_name},
                       headers={'X-AjaxPro-Method': 'PecActualizar', 'referer': self._home_url},
                       body=stringify_postdata(postdata), callback=self.parse_products_list)

    def build_product_detail_request(self, product_link, category_name):
        formdata = {'idArticulo': product_link.id, 'PVenta': product_link.price}
        return FormRequest(url=self._products_detail_url, method='POST',
                           meta={'category_name': category_name, 'product_link': product_link},
                           formdata=formdata, callback=self.parse_product_detail)
