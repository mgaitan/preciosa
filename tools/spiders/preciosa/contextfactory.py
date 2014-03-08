from OpenSSL import SSL
from scrapy.core.downloader.contextfactory import ScrapyClientContextFactory


class MyClientContextFactory(ScrapyClientContextFactory):
    def __init__(self):
        self.method = SSL.SSLv23_METHOD  # or SSL.SSLv3_METHOD
