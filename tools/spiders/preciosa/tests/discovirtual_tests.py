import os
import unittest
from preciosa.preciosa.spiders import discovirtual
from scrapy.http import Response, Request


def fake_response_from_file(file_name, url=None):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    """
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url)
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name

    file_content = open(file_path, 'r').read()

    response = Response(url=url,
        request=request,
        body=file_content)
    response.encoding = 'utf-8'
    return response


class DiscoVirtualSpiderTest(unittest.TestCase):
    def setUp(self):
        self.spider = discovirtual.DiscoVirtualSpider()

    def test_parse():
        pass

    def test_is_home_response(self):
        pass

    def test_is_categories_response(self):
        pass

    def test_prepare_categories_url(self):
        pass

    def test_get_categories():
        pass

    def test_build_product_detail_request():
        pass

    def test_build_products_listing_request():
        pass

    def test_parse_product_datail():
        pass

    def xtest_parse_products_list(self):
        results = self.spider.parse(fake_response_from_file('osdir/sample.html'))
        for item in results:
            self.assertIsNotNone(item['content'])
            self.assertIsNotNone(item['title'])
        self.assertEqual(len(results), 20)


def test_parse_line():
    pass


def test_parse_categories():
    pass


def test_get_date():
    pass


def test_stringify_post_data():
    pass


def test_get_next_page():
    pass


def test_get_product_data():
    pass
