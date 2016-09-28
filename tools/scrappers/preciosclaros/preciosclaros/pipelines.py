# -*- coding: utf-8 -*-

from scrapy.exceptions import DropItem
from preciosclaros.items import PrecioItem

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
    	if isinstance(item, PrecioItem):
    		return item 

        if item.get('id') in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item.get('id'))
            return item